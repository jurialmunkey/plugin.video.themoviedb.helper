from copy import deepcopy
from tmdbhelper.lib.api.mapping import set_show, get_empty_item
from tmdbhelper.lib.api.kodi.rpc import (
    get_kodi_library, get_movie_details, get_tvshow_details, get_episode_details,
    get_season_details, get_movie_list_details, get_tvshow_list_details,
)


class KodiDb():
    def __init__(self, tmdb_type):
        self.kodi_db_tv = {}
        self.kodi_db = get_kodi_library(tmdb_type)
        self.prepared_details = {}

    def get_dbid(self, li):
        return self.kodi_db.get_info(
            info='dbid',
            imdb_id=li.unique_ids.get('imdb'),
            tmdb_id=li.unique_ids.get('tmdb'),
            tvdb_id=li.unique_ids.get('tvdb'),
            originaltitle=li.infolabels.get('originaltitle'),
            title=li.infolabels.get('title'),
            year=li.infolabels.get('year'))

    def prepare_listitems(self, items):
        # Prepared details belong to this retrieval, including repeated use of a container.
        self.prepared_details = {}
        if not self.kodi_db:
            return
        self.prepare_item_type(items, 'movie', get_movie_list_details)
        self.prepare_item_type(items, 'tvshow', get_tvshow_list_details)

    def prepare_item_type(self, items, mediatype, getter):
        items = (li for li in items if li.infolabels.get('mediatype') == mediatype)
        dbids = {dbid for dbid in (self.get_dbid(li) for li in items) if dbid}
        if len(dbids) < 2:
            return
        titles = list(dict.fromkeys(
            item['title'] for item in self.kodi_db.database
            if item['dbid'] in dbids and item['title'] is not None))
        self.prepared_details.update({
            (mediatype, dbid): details
            for dbid, details in getter(titles, dbids).items()
        })

    def get_prepared_details(self, mediatype, dbid, getter):
        try:
            details = self.prepared_details[(mediatype, dbid)]
        except KeyError:
            # The library index may predate a rename or a library update.
            return getter(dbid)
        return deepcopy(details)

    def get_movie_details(self, dbid):
        return self.get_prepared_details('movie', dbid, get_movie_details)

    def get_tvshow_details(self, dbid):
        return self.get_prepared_details('tvshow', dbid, get_tvshow_details)

    def get_kodi_details(self, li):
        """ Pass through listitem to get Kodi details """

        def _get_tvshow_dbid():
            """ Get dbid for parent tvshow """
            return self.kodi_db.get_info(
                info='dbid',
                imdb_id=li.unique_ids.get('tvshow.imdb'),
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                tvdb_id=li.unique_ids.get('tvshow.tvdb'),
                title=li.infolabels.get('tvshowtitle'))

        def _get_child_details():
            season, episode = li.infolabels.get('season'), li.infolabels.get('episode')

            library, func = 'season', get_season_details
            if episode is not None:
                library, func = 'episode', get_episode_details

            kodi_db_tv = self.kodi_db_tv.setdefault(dbid, get_kodi_library(library, dbid))
            child_dbid = kodi_db_tv.get_info('dbid', season=season, episode=episode)
            if not child_dbid:
                return

            details = func(child_dbid)
            details['infoproperties']['tvshow.dbid'] = dbid
            return details

        if not self.kodi_db:
            return

        routes = {
            'movie': {
                'get_dbid': lambda: self.get_dbid(li),
                'get_details': self.get_movie_details},
            'tvshow': {
                'get_dbid': lambda: self.get_dbid(li),
                'get_details': self.get_tvshow_details},
            'season': {
                'get_dbid': _get_tvshow_dbid,
                'get_details': lambda x: set_show(_get_child_details() or get_empty_item(), get_tvshow_details(x))},
            'episode': {
                'get_dbid': _get_tvshow_dbid,
                'get_details': lambda x: set_show(_get_child_details() or get_empty_item(), get_tvshow_details(x))}}
        try:
            route = routes[li.infolabels['mediatype']]
        except KeyError:
            return

        dbid = route['get_dbid']()
        if not dbid:
            return
        return route['get_details'](dbid)
