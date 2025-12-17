from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.files.dbfunc import DatabaseConnection
from tmdbhelper.lib.addon.logger import TimerList
from tmdbhelper.lib.addon.thread import ParallelThread
import itertools


class ListItemConfig:
    listitem_cacher_permitted_types = ('movie', 'tvshow', 'season', 'episode', 'person', 'set')

    def __init__(self, parent, item):
        if parent.__class__.__name__ != 'ListItemDetails':
            raise Exception(f'Requires ListItemDetails parent but {parent.__class__.__name__} given')
        self.item = item
        self.next_page = bool('next_page' in item)
        self.parent = parent
        self.item['parent_params'] = self.parent.parent_params

    @cached_property
    def is_cacheable(self):
        if self.next_page:
            return False
        if self.mediatype not in self.listitem_cacher_permitted_types:
            return False
        if not self.tmdb_id:
            return False
        if not self.tmdb_type:
            return False
        return True

    @cached_property
    def listitem_cacher(self):
        if not self.is_cacheable:
            return
        return ListItemCacher(
            self.parent,
            self.tmdb_type,
            self.tmdb_id,
            self.season,
            self.episode
        )

    @cached_property
    def listitem(self):
        return ListItem(**self.item)

    def get_configured_listitem(self, data):
        if self.next_page and not self.parent.pagination:
            return
        self.listitem.set_details(data, override=True, reverse_artwork=True) if data else None
        return self.listitem

    @cached_property
    def mediatype(self):
        if self.listitem.infoproperties.get('tmdb_type') == 'person':
            return 'person'
        return self.listitem.infolabels.get('mediatype')

    @cached_property
    def tmdb_id(self):
        if self.mediatype == 'movie':
            return self.listitem.unique_ids.get('tmdb')
        if self.mediatype == 'tvshow':
            return self.listitem.unique_ids.get('tmdb') or self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'season':
            return self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'episode':
            return self.listitem.unique_ids.get('tvshow.tmdb')
        if self.mediatype == 'person':
            return self.listitem.unique_ids.get('tmdb') or self.listitem.infoproperties.get('tmdb_id')
        if self.mediatype == 'set':
            return self.listitem.unique_ids.get('tmdb')
        return

    @cached_property
    def tmdb_type(self):
        if self.mediatype == 'movie':
            return 'movie'
        if self.mediatype == 'tvshow':
            return 'tv'
        if self.mediatype == 'season':
            return 'tv'
        if self.mediatype == 'episode':
            return 'tv'
        if self.mediatype == 'person':
            return 'person'
        if self.mediatype == 'set':
            return 'collection'
        return

    @cached_property
    def season(self):
        if self.mediatype not in ('episode', 'season'):
            return
        return self.listitem.infolabels.get('season', 0)

    @cached_property
    def episode(self):
        if self.mediatype != 'episode':
            return
        return self.listitem.infolabels.get('episode', 0)

    @cached_property
    def db_cache(self):
        if not self.baseitem_db_cache_func:
            return
        return self.baseitem_db_cache_func(self.mediatype, self.tmdb_id, self.season, self.episode)

    def get_cached_item(self, connection):
        if not self.listitem_cacher:
            return
        return self.listitem_cacher.get_cached_item(connection)

    def try_queued_data(self):
        if not self.listitem_cacher:
            return
        return self.listitem_cacher.try_queued_data()


class ListItemCacher:
    def __init__(self, parent, tmdb_type, tmdb_id, season=None, episode=None, listitem_config=None):
        if parent.__class__.__name__ != 'ListItemDetails':
            raise Exception(f'Requires ListItemDetails parent but {parent.__class__.__name__} given')
        self.parent = parent  # ListItemDetails instance
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.common_apis = self.parent.common_apis
        self.extendedinfo = self.parent.extendedinfo
        self.cache = self.parent.cache
        self.listitem_config = listitem_config

    @cached_property
    def mediatype(self):
        return convert_type(self.tmdb_type, output='dbtype', season=self.season, episode=self.episode)

    @cached_property
    def baseitem_db_cache(self):
        try:
            baseitem_db_cache = BaseItemFactory(self.mediatype)
            baseitem_db_cache.tmdb_id = self.tmdb_id
            baseitem_db_cache.season = self.season
            baseitem_db_cache.episode = self.episode
            baseitem_db_cache.common_apis = self.common_apis
            baseitem_db_cache.extendedinfo = self.extendedinfo
            baseitem_db_cache.cache = self.cache
        except(AttributeError, TypeError, KeyError):
            return

        return baseitem_db_cache

    def add_item_details(self, data):
        try:
            data['infoproperties']['dbtype'] = self.mediatype
            data['infoproperties']['tmdb_type'] = self.tmdb_type
            data['infoproperties']['tmdb_id'] = self.tmdb_id
            data['label'] = data['infolabels']['title']
        except(AttributeError, TypeError, KeyError):
            pass
        return data

    def get_item(self, connection, cache_refresh=None):
        if not self.baseitem_db_cache:
            return
        self.baseitem_db_cache.connection = connection
        self.baseitem_db_cache.cache_refresh = cache_refresh
        return self.add_item_details(self.baseitem_db_cache.data)

    def get_cached_item(self, connection):
        if not self.baseitem_db_cache:
            return
        self.baseitem_db_cache.connection = connection
        self.baseitem_db_cache.cache_refresh = self.parent.cache_refresh
        return self.add_item_details(self.baseitem_db_cache.get_cached_data())

    def try_queued_data(self):
        if not self.baseitem_db_cache:
            return
        # self.baseitem_db_cache.connection = connection
        self.baseitem_db_cache.cache_refresh = (
            self.parent.cache_refresh if self.parent.cache_refresh in ('basic', 'langs')
            else None
        )
        return self.baseitem_db_cache.try_cached_data(return_queue=True)


class ListItemThread:
    def __init__(self, parent, items):
        if parent.__class__.__name__ != 'ListItemDetails':
            raise Exception(f'Requires ListItemDetails parent but {parent.__class__.__name__} given')
        self.parent = parent  # ListItemDetails instance
        self.items = items
        self.connection = self.parent.connection
        self.log_timers = self.parent.log_timers
        self.timer_lists = self.parent.timer_lists

    @cached_property
    def cached_data(self):
        with TimerList(self.timer_lists, ' - cached', log_threshold=0.001, logging=self.log_timers):
            with self.connection.open():
                return self.get_cached_data()

    def get_cached_data(self):
        return [
            listitem_config.get_cached_item(self.connection)
            for listitem_config in self.items
        ]

    @cached_property
    def uncached_items(self):
        return self.get_uncached_items()

    def get_uncached_items(self):
        return [
            self.items[x] for x, cached_item in enumerate(self.cached_data)
            if cached_item is None and self.items[x].is_cacheable
        ]

    @cached_property
    def configured_list(self):
        return self.get_configured_list()

    def get_configured_list(self):
        return [
            listitem_config.get_configured_listitem(self.cached_data[x])
            for x, listitem_config in enumerate(self.items)
        ]

    @cached_property
    def func_queue(self):
        with TimerList(self.timer_lists, ' - online', log_threshold=0.001, logging=self.log_timers):
            return self.get_func_queue()

    def get_func_queue(self):

        def _queued_data(listitem_config):
            return listitem_config.try_queued_data()

        with ParallelThread(self.uncached_items, _queued_data) as pt:
            item_queue = pt.queue

        return list(itertools.chain.from_iterable((i for i in item_queue if i)))

    def set_func_queue(self):
        self.connection.open_connection.execute('BEGIN')
        with TimerList(self.timer_lists, ' - writer', log_threshold=0.001, logging=self.log_timers):
            for func, args, kwgs in self.func_queue:
                func(*args, **kwgs)
        with TimerList(self.timer_lists, ' - commit', log_threshold=0.001, logging=self.log_timers):
            self.connection.open_connection.execute('COMMIT')
        with TimerList(self.timer_lists, ' - return', log_threshold=0.001, logging=self.log_timers):
            self.cached_data = self.get_cached_data()

    @cached_property
    def configured_items(self):
        if self.parent.cache_refresh == 'never':
            return self.configured_list
        if not self.uncached_items:
            return self.configured_list
        if not self.func_queue:
            return self.configured_list
        with self.connection.open():
            self.set_func_queue()
        return self.configured_list


class ListItemDetails:
    pagination = False
    cache_refresh = None
    extendedinfo = False
    parent_params = {}
    timer_lists = {}
    log_timers = False

    def __init__(self, common_apis=None):
        self.common_apis = common_apis or CommonContainerAPIs()
        self.cache = ItemDetailsDatabase()

    @cached_property
    def connection(self):
        return DatabaseConnection(self.cache)

    def get_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        return ListItemCacher(self, tmdb_type, tmdb_id, season, episode).get_item(
            connection=self.connection, cache_refresh=self.cache_refresh)

    def configure_listitems_threaded(self, items):
        return ListItemThread(self, [ListItemConfig(self, i) for i in items]).configured_items
