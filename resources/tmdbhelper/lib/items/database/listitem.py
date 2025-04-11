from functools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.items.database.tmdbdata import ItemDetailsDataBaseCacheFactory


# @property
# def lidc(self):
#     try:
#         return self._lidc
#     except AttributeError:
#         from tmdbhelper.lib.items.database.listitem import ListItemDetailsConfigurator
#         self._lidc = ListItemDetailsConfigurator(tmdb_api=self.tmdb_api)
#         return self._lidc


class ListItemDetailsConfigurator:
    def __init__(self, tmdb_api=None):
        self._tmdb_api = tmdb_api

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return self._tmdb_api or TMDb()

    def get_db_cache(self, mediatype):
        dbc = ItemDetailsDataBaseCacheFactory(mediatype)
        dbc.tmdb_api = self.tmdb_api
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

    def configure_listitems_threaded(self, items):
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread(items, self.configure_listitem) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    def configure_listitems(self, items):
        return [j for j in (self.configure_listitem(i) for i in items if i) if j]
