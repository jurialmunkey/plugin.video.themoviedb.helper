from xbmcgui import Dialog, INPUT_ALPHANUM
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, convert_type, get_localized, get_setting
from tmdbhelper.lib.files.hcache import set_search_history, get_search_history
from tmdbhelper.lib.items.container import ContainerDirectory
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import merge_two_dicts, try_int
from urllib.parse import urlencode


class ListSearchDir(ContainerDirectory):

    @staticmethod
    def get_searchdir(tmdb_type, clear_cache_item=True, append_type=False, **kwargs):  # list_searchdir
        base_item = {
            'label': f'{get_localized(137)} {convert_type(tmdb_type, "plural")}',
            'art': {'thumb': f'{ADDONPATH}/resources/icons/themoviedb/search.png'},
            'infoproperties': {'specialsort': 'top'},
            'params': merge_two_dicts(kwargs, {'info': 'search', 'tmdb_type': tmdb_type})}
        items = []
        items.append(base_item)

        history = get_search_history(tmdb_type)
        history.reverse()

        for i in history:
            item = {
                'label': f'{i} ({tmdb_type})' if append_type else i,
                'art': base_item.get('art'),
                'params': merge_two_dicts(base_item.get('params', {}), {'query': i})}
            items.append(item)

        if history and clear_cache_item:
            item = {
                'label': get_localized(32121),
                'art': base_item.get('art'),
                'infoproperties': {'specialsort': 'bottom'},
                'params': merge_two_dicts(base_item.get('params', {}), {'info': 'dir_search', 'clear_cache': 'True'})}
            items.append(item)

        return items

    def get_items(self, tmdb_type, **kwargs):  # list_searchdir_router
        self.plugin_category = get_localized(137)
        if kwargs.get('clear_cache') != 'True':
            return self.get_searchdir(tmdb_type, **kwargs)
        set_search_history(tmdb_type, clear_cache=True)
        self.container_refresh = True


class ListMultiSearchDir(ListSearchDir):

    multi_search_types = ('movie', 'tv', 'person', 'both', 'collection', 'company', 'keyword')

    @staticmethod
    def get_zippered_list(lists):
        max_len = 0
        for i in lists:
            max_len = max(max_len, len(i))
        return [i[x] for x in range(max_len) for i in lists if x < len(i)]

    def get_multisearchdir(self):
        lists = [
            self.get_searchdir(i, clear_cache_item=False, append_type=True)
            for i in self.multi_search_types
        ]
        items = self.get_zippered_list(lists)

        if len(items) > len(self.multi_search_types):  # We have search results so need clear cache item
            items.append({
                'label': get_localized(32121),
                'art': {'thumb': f'{ADDONPATH}/resources/icons/themoviedb/search.png'},
                'infoproperties': {'specialsort': 'bottom'},
                'params': {'info': 'dir_multisearch', 'clear_cache': 'True'}})

        return items

    def get_items(self, **kwargs):
        self.plugin_category = get_localized(137)

        if kwargs.get('clear_cache') != 'True':
            return self.get_multisearchdir()

        for tmdb_type in self.multi_search_types:
            set_search_history(tmdb_type, clear_cache=True)

        self.container_refresh = True


class ListSearchProperties(ListStandardProperties):
    @cached_property
    def cache_name_tuple(self):
        return (
            self.class_name,
            self.query,
            self.tmdb_type,
            self.page,
            self.pmax,
        )

    def get_search_query(self):
        from tmdbhelper.lib.addon.consts import PARAM_WIDGETS_RELOAD_FORCED

        if self.reload == PARAM_WIDGETS_RELOAD_FORCED:
            return

        return set_search_history(
            query=Dialog().input(get_localized(32044), type=INPUT_ALPHANUM),
            tmdb_type=self.tmdb_type)

    def set_search_query(self):
        set_search_history(query=self.query, tmdb_type=self.tmdb_type)

    @cached_property
    def query(self):
        return self.original_query or self.get_search_query()  # QUERY new query from keyboard if we dont have one


class ListSearch(ListStandard):

    list_properties_class = ListSearchProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'search/{tmdb_type}?{paramstring}'
        list_properties.localize = 137
        list_properties.page_length = get_setting('pagemulti_tmdb', 'int') or 1
        return list_properties

    def get_items(self, tmdb_type, query=None, page=1, length=None, update_listing=False, **kwargs):
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.original_query = query or ''
        self.list_properties.reload = kwargs.get('reload')

        if not self.list_properties.query:
            return

        # FORCE history to be saved
        if self.list_properties.query and kwargs.get('history', '').lower() == 'true':
            self.list_properties.set_search_query()

        request_kwgs = {
            'query': self.list_properties.query,
            'year': kwargs.get('year'),
            'first_air_date_year': kwargs.get('first_air_date_year'),
            'primary_release_year': kwargs.get('primary_release_year')
        }

        # MULTI search if searching for both movies and tv
        self.list_properties.url = self.list_properties.request_url.format(
            tmdb_type='multi' if self.list_properties.tmdb_type == 'both' else self.list_properties.tmdb_type,
            paramstring=urlencode(request_kwgs)
        )

        self.list_properties.page = try_int(page) or 1
        self.list_properties.length = try_int(length)

        if not self.list_properties.original_query:
            params = merge_two_dicts(kwargs, {
                'info': 'search',
                'tmdb_type': self.list_properties.tmdb_type,
                'page': self.list_properties.page,
                'query': self.list_properties.query,
                'update_listing': 'True'})
            self.container_update = f'{PLUGINPATH}?{urlencode(params)}'
            self.parent_params = params
            # Trigger container update using new path with query after adding items
            # Prevents onback from re-prompting for user input by re-writing path

        self.update_listing = True if update_listing else False
        self.list_properties.plugin_name = f'{{localized}} - {self.list_properties.query.capitalize()} ({{plural}})'
        return self.get_items_finalised()
