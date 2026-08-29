from tmdbhelper.lib.items.directories.lists_default import UncachedItemsPage
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.items.directories.trakt.mapper_standard import FactoryItemMapper
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class UncachedTraktItemsPage(UncachedItemsPage):
    @cached_property
    def response_results(self):
        try:
            return self.response.json()
        except (TypeError, KeyError, AttributeError):
            return

    @cached_property
    def response_total_pages(self):
        return try_int(self.response.headers.get('x-pagination-page-count', 0))

    @cached_property
    def response_total_items(self):
        return try_int(self.response.headers.get('x-pagination-item-count', 0))


class ListTraktStandardProperties(ListStandardProperties):

    class_pages = UncachedTraktItemsPage
    trakt_filters = {}
    trakt_authorization = False

    sub_type = False
    sub_type_map = {
        'movie': 'movie',
        'tv': 'show',
    }

    @property
    def next_page(self):
        return self.page + 1

    @cached_property
    def limit(self):
        return self.pmax * 20

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = self.get_cache_name_list_filter()
        cache_name_tuple = self.get_cache_name_list_prefix() + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.limit]
        return tuple(cache_name_tuple)

    def get_cache_name_list_filter(self):
        cache_name_list = [f'{k}={v}' for k, v in self.trakt_filters.items()]
        cache_name_list = sorted(cache_name_list)
        return cache_name_list

    def get_cache_name_list_prefix(self):
        return [self.class_name, self.tmdb_type]

    @cached_property
    def trakt_type(self):
        return self.sub_type_map.get(self.tmdb_type)

    @cached_property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    @cached_property
    def final_items(self):
        return self.class_pages(self, self.page).items

    def get_uncached_items(self):
        return {
            'items': self.final_items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_api_response(self, page=1):
        if self.trakt_authorization and not self.trakt_api.is_authorized:
            return
        return self.trakt_api.get_response(self.url, page=page, limit=self.limit, **self.trakt_filters)

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryItemMapper(item, add_infoproperties, trakt_type=self.trakt_type, sub_type=self.sub_type).item


class ListTraktStandardLocalProperties(ListTraktStandardProperties):
    page_limit = 8
    item_limit = 20

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = self.get_cache_name_list_filter()
        cache_name_tuple = ['local_items'] + self.get_cache_name_list_prefix() + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.limit, self.page_limit, self.item_limit]
        return tuple(cache_name_tuple)

    @property
    def next_page(self):
        return self.pages + 1  # Override next page object by making next_page out of bounds

    @cached_property
    def next_page_generator(self):
        return (x for x in range(self.page, self.page + self.page_limit))

    @cached_property
    def kodi_db(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library(self.tmdb_type)

    def get_dbid(self, item):
        if not self.kodi_db:
            return
        try:
            unique_ids = item['unique_ids']
            infolabels = item['infolabels']
        except (KeyError, TypeError):
            return
        return self.kodi_db.get_info(
            info='dbid',
            imdb_id=unique_ids.get('imdb'),
            tmdb_id=unique_ids.get('tmdb'),
            tvdb_id=unique_ids.get('tvdb'),
            originaltitle=infolabels.get('originaltitle'),
            title=infolabels.get('title'),
            year=infolabels.get('year')
        )

    @cached_property
    def item_generator(self):
        return (
            i for xpage in self.next_page_generator
            for i in self.class_pages(self, xpage).items
            if i and self.get_dbid(i)
        )

    @cached_property
    def final_items(self):
        final_items = []
        for x, i in enumerate(self.item_generator):
            if x >= self.item_limit:
                break
            final_items.append(i)
        return final_items


class ListTraktStandard(ListStandard):

    @property
    def list_properties_class(self):
        if not self.is_localonly:
            return ListTraktStandardProperties
        return ListTraktStandardLocalProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties


class ListTraktBoxOffice(ListTraktStandard):  # Box Office doesn't support filters or pagination
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = '{trakt_type}s/boxoffice'
        list_properties.localize = 32207
        list_properties.sub_type = True
        return list_properties


class ListTraktRecommendations(ListTraktStandard):  # Box Office doesn't support filters or pagination
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.trakt_filters = {
            'ignore_collected': 'true',
            'ignore_watchlisted': 'true'
        }
        list_properties.request_url = 'recommendations/{trakt_type}s'
        list_properties.localize = 32198
        list_properties.sub_type = True
        return list_properties
