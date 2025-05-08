from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.files.dbfunc import DatabaseConnection
from tmdbhelper.lib.addon.logger import TimerList
from tmdbhelper.lib.addon.thread import ParallelThread


class ListItemConfig:
    def __init__(self, item):
        self.item = item

    @cached_property
    def listitem(self):
        return ListItem(**self.item)

    def get_configured_listitem(self, data):
        self.listitem.set_details(data, override=True) if data else None
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


class ListItemCacher:
    def __init__(self, parent, tmdb_type, tmdb_id, season=None, episode=None):
        self.parent = parent  # ListItemDetails instance
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.common_apis = self.parent.common_apis
        self.extendedinfo = self.parent.extendedinfo
        self.cache = self.parent.cache

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
        self.baseitem_db_cache.cache_refresh = None
        return self.baseitem_db_cache.try_cached_data(return_queue=True)


def ListItemCacherFactory(self, listitem_config):
    if listitem_config.__class__.__name__ != 'ListItemConfig':
        return
    if not listitem_config.tmdb_id:
        return
    if not listitem_config.tmdb_type:
        return
    if listitem_config.tmdb_type not in ('movie', 'tv', 'season', 'episode', 'person'):
        return
    return ListItemCacher(
        self, listitem_config.tmdb_type, listitem_config.tmdb_id,
        listitem_config.season, listitem_config.episode)


class ListItemDetails:
    pagination = False
    cache_refresh = None
    extendedinfo = False
    timer_lists = {}
    timer_log = False

    def __init__(self, common_apis=None):
        self.common_apis = common_apis or CommonContainerAPIs()
        self.cache = ItemDetailsDatabase()

    @cached_property
    def connection(self):
        return DatabaseConnection(self.cache)

    def get_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        return ListItemCacher(self, tmdb_type, tmdb_id, season, episode).get_item(
            connection=self.connection, cache_refresh=self.cache_refresh)

    # def get_listitem(self, i):
    #     i['parent_params'] = self.parent_params
    #     if 'next_page' in i:
    #         return ListItem(**i) if self.pagination else None
    #     listitem_config = ListItemConfig(i)
    #     baseitem_dbdata = self.get_item(listitem_config.tmdb_type, listitem_config.tmdb_id, listitem_config.season, listitem_config.episode)
    #     return listitem_config.get_configured_listitem(baseitem_dbdata)

    def configure_listitem(self, i):
        i['parent_params'] = self.parent_params

        listitem_config = ListItemConfig(i) if 'next_page' not in i else ListItem(**i) if self.pagination else None
        listitem_cacher = ListItemCacherFactory(self, listitem_config)

        return (listitem_config, listitem_cacher)

    def configure_listitems_threaded(self, items):
        items = [j for j in (self.configure_listitem(i) for i in items) if j]

        with TimerList(self.timer_lists, ' - cached', log_threshold=0.05, logging=self.log_timers):
            with self.connection.open():
                previously_cached_items = [
                    listitem_cacher.get_cached_item(self.connection) if listitem_cacher else None
                    for listitem_config, listitem_cacher in items
                ]

            uncached_items = [
                items[x] for x, i in enumerate(previously_cached_items)
                if i is None and items[x] and items[x][1]
            ]

        def _configure_list(cache_items):
            return [
                listitem_config.get_configured_listitem(cache_items[x] if listitem_cacher else None)
                if listitem_config.__class__.__name__ == 'ListItemConfig' else listitem_config
                for x, (listitem_config, listitem_cacher) in enumerate(items) if listitem_config
            ]

        if not uncached_items or self.cache_refresh == 'never':
            return _configure_list(previously_cached_items)

        def _queued_data(i):
            if not i or not i[1]:
                return
            return i[1].try_queued_data()

        with TimerList(self.timer_lists, ' - online', log_threshold=0.05, logging=self.log_timers):
            with ParallelThread(uncached_items, _queued_data) as pt:
                item_queue = pt.queue

        func_queue = []
        for i in item_queue:
            if not i:
                continue
            func_queue.extend(i)

        if not func_queue:
            return _configure_list(previously_cached_items)

        # from tmdbhelper.lib.addon.logger import CProfiler
        # with CProfiler('profilers'):
        with self.connection.open():
            self.connection.open_connection.execute('BEGIN')
            with TimerList(self.timer_lists, ' - writer', log_threshold=0.05, logging=self.log_timers):
                for func, args, kwgs in func_queue:
                    func(*args, **kwgs)
            with TimerList(self.timer_lists, ' - commit', log_threshold=0.05, logging=self.log_timers):
                self.connection.open_connection.execute('COMMIT')
            with TimerList(self.timer_lists, ' - return', log_threshold=0.05, logging=self.log_timers):
                previously_cached_items = [
                    listitem_cacher.get_cached_item(self.connection) if listitem_cacher else None
                    for listitem_config, listitem_cacher in items
                ]

        return _configure_list(previously_cached_items)
