from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, use_item_cache
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type, get_localized
from tmdbhelper.lib.items.filters import is_excluded
from jurialmunkey.parser import try_int


class ListProperties:

    plugin_name = ''
    localize = None
    tmdb_type = None
    items = None
    url = None
    params = {}
    filters = {}
    sorted_function = None
    sorted_reversed = None

    @cached_property
    def plural(self):
        return convert_type(self.tmdb_type, 'plural')

    @cached_property
    def localized(self):
        return get_localized(self.localize) if self.localize else ''

    @cached_property
    def plugin_category(self):
        return self.plugin_name.format(localized=self.localized, plural=self.plural)

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container', items=self.items)

    @cached_property
    def filtered_items(self):
        if not self.filters:
            return self.items
        return [
            i for i in self.items
            if not is_excluded(i, **self.filters)
        ]

    @cached_property
    def sorted_items(self):
        if not self.sorted_function:
            return self.filtered_items
        return sorted(self.filtered_items, key=self.sorted_function, reverse=self.sorted_reversed)

    @property
    def finalised_items(self):
        return self.sorted_items


class ListDefault(ContainerDefaultCacheDirectory):

    list_properties_class = ListProperties

    @cached_property
    def list_properties(self):
        list_properties = self.list_properties_class()
        return self.configure_list_properties(list_properties)

    def configure_list_properties(self, list_properties):
        list_properties.plugin_name = '{localized} {plural}'
        list_properties.localize = None
        list_properties.request_url = ''  # PATH to request
        list_properties.results_key = 'results'  # KEY in RESPONSE from PATH holding ITEMS
        list_properties.dbid_sorted = False
        list_properties.sorted_reversed = False
        list_properties.sorted_function = None
        list_properties.filters = self.filters
        return list_properties

    @cached_property
    def sort_by_dbid(self):
        if not self.kodi_db:
            return False
        if not self.list_properties.dbid_sorted:
            return False
        return True

    @cached_property
    def kodi_db(self):
        return self.get_kodi_database(self.list_properties.tmdb_type)

    @use_item_cache('ItemContainer.db')
    def get_cached_items(self, *args, **kwargs):
        return self._get_cached_items(*args, **kwargs)

    def _get_cached_items(self, *args, **kwargs):
        return

    @use_item_cache('ItemContainer.db')
    def get_cached_items_page(self, *args, **kwargs):
        return self._get_cached_items_page(*args, **kwargs)

    def _get_cached_items_page(self, *args, **kwargs):
        return

    def get_request_url(self, tmdb_type, **kwargs):
        return self.list_properties.request_url.format(tmdb_type=tmdb_type)

    def get_items(self, tmdb_type, page=1, length=None, **kwargs):
        self.list_properties.url = self.get_request_url(tmdb_type=tmdb_type, **kwargs)
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.length = try_int(length) or 1
        self.list_properties.page = try_int(page) or 1
        self.list_properties.items = self.get_cached_items(
            self.list_properties.url,
            self.list_properties.tmdb_type,
            page=self.list_properties.page,
            length=self.list_properties.length,
            paginated=self.pagination
        )
        return self.get_items_finalised()

    def get_items_finalised(self):
        self.container_content = self.list_properties.container_content
        self.plugin_category = self.list_properties.plugin_category
        return self.list_properties.finalised_items
