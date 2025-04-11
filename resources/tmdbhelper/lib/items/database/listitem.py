from functools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.items.database.tmdbdata import ItemDetailsDataBaseCacheFactory


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
