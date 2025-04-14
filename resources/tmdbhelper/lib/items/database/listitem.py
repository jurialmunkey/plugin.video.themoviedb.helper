from functools import cached_property
from threading import Lock
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.items.database.tmdbdata import ItemDetailsDataBaseCacheFactory


# @cached_property
# def lidc(self):
#     from tmdbhelper.lib.items.database.listitem import ListItemDetailsConfigurator
#     return ListItemDetailsConfigurator(tmdb_api=self.tmdb_api)


class ThreadLocks(dict):
    def __missing__(self, key):
        self[key] = Lock()
        return self[key]


class ListItemDetailsConfigurator:
    def __init__(self, tmdb_api=None):
        self._tmdb_api = tmdb_api

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return self._tmdb_api or TMDb()

    @cached_property
    def thread_locks(self):
        return ThreadLocks()

    def get_db_cache(self, mediatype):
        dbc = ItemDetailsDataBaseCacheFactory(mediatype)
        dbc.tmdb_api = self.tmdb_api
        dbc.thread_locks = self.thread_locks
        return dbc

    def get_configured_db_cache(self, li):
        mediatype = li.infolabels.get('mediatype')

        if mediatype not in ('movie', 'tvshow', 'season', 'episode'):
            return

        dbc = self.get_db_cache(mediatype)
        dbc.tmdb_id = li.unique_ids.get('tmdb')

        if mediatype not in ('season', 'episode'):
            return dbc

        dbc.season = li.infolabels.get('season', 0)
        dbc.tmdb_id = li.unique_ids.get('tvshow.tmdb')

        if mediatype != 'episode':
            return dbc

        dbc.episode = li.infolabels.get('episode')
        return dbc

    def configure_listitem(self, i):
        li = ListItem(**i)
        dbc = self.get_configured_db_cache(li)

        if not dbc:
            return li

        with dbc.cache.get_database() as dbc.connection:
            db_cache_data = dbc.data

        if not db_cache_data:
            return li

        li.set_details(db_cache_data, override=True)

        # li.art = self.get_item_artwork(item['artwork'], is_season=mediatype in ['season', 'episode'])
        return li

    def configure_listitems_threaded(self, items):  # TODO: Retrieve sequentially then pool unavailable items and thread lookups before setting sequentially
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(items, self.configure_listitem) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    def configure_listitems(self, items):
        return [j for j in (self.configure_listitem(i) for i in items if i) if j]
