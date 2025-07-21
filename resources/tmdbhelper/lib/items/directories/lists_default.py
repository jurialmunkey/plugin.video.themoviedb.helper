from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type, get_localized
from tmdbhelper.lib.items.filters import is_excluded
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
