from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties, UncachedItemsPage
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


PAGES_LENGTH = get_setting('pagemulti_trakt', 'int') or 1


class UncachedTraktItemsPage(UncachedItemsPage):
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def results(self):
        try:
            results = self.response.json()
        except (TypeError, KeyError):
            return []
        try:
            self.outer_class.total_pages = try_int(self.response.headers.get('x-pagination-page-count', 0))
            self.outer_class.total_items = try_int(self.response.headers.get('x-pagination-item-count', 0))
        except (TypeError, KeyError):
            self.outer_class.total_pages = 0
            self.outer_class.total_items = 0
        return results


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
        return self.length * 20

    @cached_property
    def cache_name(self):
        return '_'.join(map(str, self.cache_name_tuple))

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = [f'{k}={v}' for k, v in self.trakt_filters.items()]
        cache_name_tuple = sorted(cache_name_tuple)
        cache_name_tuple = [self.class_name, self.tmdb_type] + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.limit]
        return tuple(cache_name_tuple)

    @cached_property
    def trakt_type(self):
        return self.sub_type_map[self.tmdb_type]

    @cached_property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    @cached_property
    def mapper(self):
        from tmdbhelper.lib.api.trakt.mapping import ItemMapper
        return ItemMapper()

    def get_uncached_items(self):
        return {
            'items': self.class_pages(self, self.page).items,
            'pages': self.total_pages,
            'count': self.total_items,
        }

    def get_uncached_response(self, page=1):
        if self.trakt_authorization and not self.trakt_api.authorization:
            if self.trakt_api.attempted_login or not self.trakt_api.authorize(login=True):
                return
        return self.trakt_api.get_response(self.url, page=page, limit=self.limit, **self.trakt_filters)

    def get_sub_typed_item(self, item):
        if not self.sub_type:
            return item
        item.update(item.pop(self.trakt_type, {}))
        return item

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.mapper.get_info(
            self.get_sub_typed_item(item),
            self.tmdb_type,
            add_infoproperties=add_infoproperties)


class ListTraktStandard(ListStandard):

    list_properties_class = ListTraktStandardProperties

    def get_items(self, *args, length=None, tmdb_type=None, **kwargs):
        length = try_int(length) or PAGES_LENGTH
        return super().get_items(*args, length=length, tmdb_type=tmdb_type, **kwargs)


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
