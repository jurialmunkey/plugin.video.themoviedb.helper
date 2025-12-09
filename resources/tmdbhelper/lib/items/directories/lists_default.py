from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory
from tmdbhelper.lib.addon.plugin import convert_type, get_localized
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class ItemCache:
    def __init__(self, filename):
        from tmdbhelper.lib.files.bcache import BasicCache
        self.cache = BasicCache(filename=filename)

    def __call__(self, function):
        def wrapper(instance, *args, **kwargs):
            kwargs['cache_days'] = instance.cache_days
            kwargs['cache_name'] = instance.cache_name
            kwargs['cache_combine_name'] = True
            return self.cache.use_cache(function, instance, *args, **kwargs)
        return wrapper


class UncachedItemsPage:
    def __init__(self, outer_class, page):
        self.outer_class = outer_class
        self.page = page

    @cached_property
    def response(self):
        return self.outer_class.get_api_response(self.page)

    @cached_property
    def response_results(self):
        try:
            return self.response[self.outer_class.results_key]
        except (TypeError, KeyError):
            return

    @cached_property
    def response_total_pages(self):
        return self.response['total_pages']

    @cached_property
    def response_total_items(self):
        return self.response['total_results']

    @cached_property
    def results(self):
        return self.get_results()

    def get_results(self):
        if not self.response_results:
            return []
        try:
            self.outer_class.total_pages = self.response_total_pages
            self.outer_class.total_items = self.response_total_items
        except (TypeError, KeyError):
            self.outer_class.total_pages = 0
            self.outer_class.total_items = 0
        return self.response_results

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return [j for j in [
            self.outer_class.get_mapped_item(i, add_infoproperties=(
                ('total_pages', self.outer_class.total_pages),
                ('total_results', self.outer_class.total_items),
                ('rank', x),
            ))
            for x, i in enumerate(self.results, 1) if i
        ] if j]


class ListProperties:

    plugin_name = ''
    localize = None
    tmdb_type = None
    params = {}
    filters = {}
    cache_days = 0.25  # 6 hours default cache
    dbid_sorted = False
    pagination = False
    is_cacheonly = True

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()

    @cached_property
    def cache_name(self):
        return '_'.join(map(str, self.cache_name_tuple))

    @cached_property
    def pmax(self):
        pmax = self.length or self.page_length or 1
        pmax = min(pmax, 8 if self.is_cacheonly else self.page_length)
        return pmax

    @cached_property
    def cache_name_tuple(self):
        return (
            self.class_name,
            self.tmdb_type,
            self.page,
            self.pmax,
        )

    @cached_property
    def unconfigured_item_data(self):
        return self.get_cached_items() or {}

    @cached_property
    def items(self):
        return self.unconfigured_item_data.get('items') or []

    @cached_property
    def pages(self):
        return self.unconfigured_item_data.get('pages') or 0

    @cached_property
    def count(self):
        return self.unconfigured_item_data.get('count') or 0

    @ItemCache('ItemContainer.db')
    def get_cached_items(self, *args, **kwargs):
        return self.get_uncached_items(*args, **kwargs)

    def get_uncached_items(self, *args, **kwargs):
        return

    @cached_property
    def url(self):
        return self.request_url.format(tmdb_type=self.tmdb_type)

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
        from tmdbhelper.lib.items.filters import is_excluded
        return [
            i for i in self.items
            if not is_excluded(i, **self.filters)
        ]

    @cached_property
    def sorted_items(self):
        return self.filtered_items

    @cached_property
    def next_page_item(self):
        return {'next_page': self.next_page}

    @cached_property
    def finalised_items(self):
        if self.pagination and self.pages and self.next_page <= self.pages:
            self.sorted_items.append(self.next_page_item)
        return self.sorted_items


class ListSliceProperties(ListProperties):
    unconfigured_item_data = None

    @cached_property
    def cache_name(self):
        return self.class_name

    @property
    def next_page(self):
        return self.page + 1

    def get_uncached_items(self):
        return

    @cached_property
    def items(self):
        return self.get_cached_items() or []

    @cached_property
    def pages(self):
        return (self.count + self.limit - 1) // self.limit  # Ceiling division

    @cached_property
    def count(self):
        return len(self.filtered_items)

    @cached_property
    def limit(self):
        return self.pmax * 20

    @cached_property
    def item_a(self):
        return max(((self.page - 1) * self.limit), 0)

    @cached_property
    def item_z(self):
        return min((self.page * self.limit), self.count)

    @cached_property
    def sorted_items(self):
        sorted_items = self.filtered_items
        return sorted_items[self.item_a:self.item_z]

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container', items=self.sorted_items)


class ListDefault(ContainerDefaultCacheDirectory):

    list_properties_class = ListProperties

    @cached_property
    def list_properties(self):
        list_properties = self.list_properties_class()
        return self.configure_list_properties(list_properties)

    def configure_list_properties(self, list_properties):
        list_properties.plugin_name = '{localized} {plural}'
        list_properties.results_key = 'results'  # KEY in RESPONSE from PATH holding ITEMS
        list_properties.filters = self.filters
        list_properties.pagination = self.pagination
        list_properties.tmdb_api = self.tmdb_api
        list_properties.trakt_api = self.trakt_api
        list_properties.is_cacheonly = self.is_cacheonly
        list_properties.class_name = f'{self.__class__.__name__}'
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

    def get_items(self, tmdb_type, page=1, length=None, **kwargs):
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.length = try_int(length)
        self.list_properties.page = try_int(page) or 1
        return self.get_items_finalised()

    def get_items_finalised(self):
        self.container_content = self.list_properties.container_content
        self.plugin_category = self.list_properties.plugin_category
        return self.list_properties.finalised_items
