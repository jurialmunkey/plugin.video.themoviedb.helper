from tmdbhelper.lib.api.contains import CommonContainerAPIs
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.files.dbfunc import DatabaseConnection


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


class ListItemCache:
    def __init__(self, parent, tmdb_type, tmdb_id, season=None, episode=None):
        self.parent = parent  # ListItemDetails instance
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.common_apis = self.parent.common_apis
        self.extendedinfo = self.parent.extendedinfo
        self.cache_refresh = self.parent.cache_refresh
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
            baseitem_db_cache.cache_refresh = self.cache_refresh
            baseitem_db_cache.cache = self.cache
        except(AttributeError, TypeError, KeyError):
            return

        try:
            baseitem_db_cache.data['infoproperties']['dbtype'] = self.mediatype
            baseitem_db_cache.data['infoproperties']['tmdb_type'] = self.tmdb_type
            baseitem_db_cache.data['infoproperties']['tmdb_id'] = self.tmdb_id
            baseitem_db_cache.data['label'] = baseitem_db_cache.data['infolabels']['title']
        except(AttributeError, TypeError, KeyError):
            return

        return baseitem_db_cache

    def get_item(self):
        if not self.baseitem_db_cache:
            return
        return self.baseitem_db_cache.data


class ListItemDetails:
    pagination = False
    cache_refresh = None
    extendedinfo = False

    def __init__(self, common_apis=None):
        self.common_apis = common_apis or CommonContainerAPIs()
        self.cache = ItemDetailsDatabase()

    @cached_property
    def connection(self):
        return DatabaseConnection(self.cache)

    def get_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        return ListItemCache(self, tmdb_type, tmdb_id, season, episode).get_item()

    def get_listitem(self, i):
        i['parent_params'] = self.parent_params
        if 'next_page' in i:
            return ListItem(**i) if self.pagination else None
        listitem_config = ListItemConfig(i)
        baseitem_dbdata = self.get_item(listitem_config.tmdb_type, listitem_config.tmdb_id, listitem_config.season, listitem_config.episode)
        return listitem_config.get_configured_listitem(baseitem_dbdata)

    def configure_listitems_threaded(self, items):
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(items, self.get_listitem) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]
