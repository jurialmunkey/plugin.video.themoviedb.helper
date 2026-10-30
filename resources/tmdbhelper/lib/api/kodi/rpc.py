from jurialmunkey.parser import try_int, find_dict_in_list
from tmdbhelper.lib.addon.thread import use_thread_lock
import jurialmunkey.jsnrpc as jurialmunkey_jsnrpc

get_library = jurialmunkey_jsnrpc.get_library
set_tags = jurialmunkey_jsnrpc.set_tags
set_watched = jurialmunkey_jsnrpc.set_watched
set_playprogress = jurialmunkey_jsnrpc.set_playprogress
get_directory = jurialmunkey_jsnrpc.get_directory


MOVIE_DETAILS_PROPERTIES = [
    "title", "genre", "year", "rating", "director", "trailer", "tagline", "plot", "plotoutline", "originaltitle",
    "writer", "studio", "mpaa", "cast", "country", "imdbnumber", "runtime", "set",
    "showlink", "streamdetails", "top250", "votes", "fanart", "thumbnail", "file", "sorttitle", "setid",
    "dateadded", "tag", "art", "userrating", "ratings", "premiered", "uniqueid"]

TVSHOW_DETAILS_PROPERTIES = [
    "title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast", "episode", "imdbnumber",
    "premiered", "votes", "fanart", "thumbnail", "file", "originaltitle", "sorttitle", "episodeguide",
    "season", "dateadded", "tag", "art", "userrating", "ratings", "runtime", "uniqueid"]


def get_jsonrpc(method=None, params=None, query_id=1):
    return jurialmunkey_jsnrpc.get_jsonrpc(method, params, query_id)


def get_kodi_library(tmdb_type, tvshowid=None, cache_refresh=False):
    if tmdb_type == 'movie':
        return KodiLibrary(dbtype='movie', cache_refresh=cache_refresh)
    if tmdb_type == 'tv':
        return KodiLibrary(dbtype='tvshow', cache_refresh=cache_refresh)
    if tmdb_type in ['season', 'episode'] and tvshowid:
        return KodiLibrary(dbtype=tmdb_type, tvshowid=tvshowid, cache_refresh=cache_refresh)
    if tmdb_type == 'both':
        return KodiLibrary(dbtype='both', cache_refresh=cache_refresh)


def get_mapped_details(details, dbid, key):
    from tmdbhelper.lib.api.kodi.mapping import ItemMapper
    details['dbid'] = dbid
    return ItemMapper(key=key).get_info(details)


def get_item_details(dbid=None, method=None, key=None, properties=None):
    if not dbid or not method or not key or not properties:
        return {}
    params = {
        f'{key}id': try_int(dbid),
        "properties": properties}
    try:
        details = get_jsonrpc(method, params)
        details = details['result'][f'{key}details']
        return get_mapped_details(details, dbid, key)
    except (AttributeError, KeyError):
        return {}


def get_movie_details(dbid=None):
    return get_item_details(
        dbid=dbid, method="VideoLibrary.GetMovieDetails",
        key="movie", properties=MOVIE_DETAILS_PROPERTIES)


def get_tvshow_details(dbid=None):
    return get_item_details(
        dbid=dbid, method="VideoLibrary.GetTVShowDetails",
        key="tvshow", properties=TVSHOW_DETAILS_PROPERTIES)


def get_list_details(titles, dbids, method, key, properties):
    """Map candidates by the Kodi IDs already selected by the library matcher."""
    if not titles or not dbids:
        return {}
    params = {
        'properties': properties,
        'filter': {'field': 'title', 'operator': 'is', 'value': titles},
    }
    response = get_jsonrpc(method, params)
    try:
        details = response['result'][f'{key}s']
    except KeyError:
        return {}
    return {
        item[f'{key}id']: get_mapped_details(item, item[f'{key}id'], key)
        for item in details if item[f'{key}id'] in dbids
    }


def get_movie_list_details(titles, dbids):
    return get_list_details(
        titles, dbids, method='VideoLibrary.GetMovies',
        key='movie', properties=MOVIE_DETAILS_PROPERTIES)


def get_tvshow_list_details(titles, dbids):
    return get_list_details(
        titles, dbids, method='VideoLibrary.GetTVShows',
        key='tvshow', properties=TVSHOW_DETAILS_PROPERTIES)


def get_season_details(dbid=None):
    properties = [
        "season", "showtitle", "episode", "fanart", "thumbnail", "tvshowid",
        "art", "userrating", "title"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetSeasonDetails", key="season", properties=properties)


def get_episode_details(dbid=None):
    properties = [
        "title", "plot", "votes", "rating", "writer", "firstaired", "runtime", "director", "productioncode",
        "season", "episode", "originaltitle", "showtitle", "cast", "streamdetails", "fanart", "thumbnail",
        "file", "tvshowid", "dateadded", "uniqueid", "art", "specialsortseason", "specialsortepisode", "userrating",
        "seasonid", "ratings"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetEpisodeDetails", key="episode", properties=properties)


THREAD_LOCK = 'TMDbHelper.KodiLibrary.ThreadLock'


class KodiLibrary(object):
    def __init__(self, dbtype=None, tvshowid=None, logging=True, cache_refresh=False):
        self._dbtype = dbtype
        self._tvshowid = tvshowid
        self._logging = logging
        self._cache_refresh = cache_refresh

    @property
    def cache(self):
        try:
            return self._cache
        except AttributeError:
            from tmdbhelper.lib.files.mcache import MemoryCache
            self._cache = MemoryCache(name='KodiLibrary')
            return self._cache

    @property
    def database(self):
        try:
            return self._database
        except AttributeError:
            self._database = self._get_cached_database()
            return self._database

    @use_thread_lock(THREAD_LOCK)
    def _get_cached_database(self):

        if self._dbtype == 'both':

            movies = self.cache.use(
                self._get_database, 'movie', None,
                cache_name='database',
                cache_minutes=180,
                cache_refresh=self._cache_refresh,
                cache_store_none=True
            ) or []

            tvshows = self.cache.use(
                self._get_database, 'tvshow', None,
                cache_name='database',
                cache_minutes=180,
                cache_refresh=self._cache_refresh,
                cache_store_none=True
            ) or []

            database = movies + tvshows

        else:

            database = self.cache.use(
                self._get_database, self._dbtype, self._tvshowid,
                cache_name='database',
                cache_minutes=180,
                cache_refresh=self._cache_refresh,
                cache_store_none=True
            )

        return database

    def _get_database(self, dbtype, tvshowid=None):

        def _get_kodi_database():
            if not dbtype:
                return []
            if dbtype == "movie":
                method = "VideoLibrary.GetMovies"
                params = {"properties": ["title", "imdbnumber", "originaltitle", "uniqueid", "year", "file"]}
            if dbtype == "tvshow":
                method = "VideoLibrary.GetTVShows"
                params = {"properties": ["title", "imdbnumber", "originaltitle", "uniqueid", "year"]}
            if dbtype == "season":
                method = "VideoLibrary.GetSeasons"
                params = {"tvshowid": tvshowid, "properties": ["title", "showtitle", "season"]}
            if dbtype == "episode":
                method = "VideoLibrary.GetEpisodes"
                params = {"tvshowid": tvshowid, "properties": ["title", "showtitle", "season", "episode", "file"]}
            try:
                response = get_jsonrpc(method, params)['result'][f'{dbtype}s'] or []
            except (KeyError, AttributeError):
                return []
            dbid_name = f'{dbtype}id'
            return [
                {
                    'imdb_id': item.get('uniqueid', {}).get('imdb'),
                    'tmdb_id': item.get('uniqueid', {}).get('tmdb'),
                    'tvdb_id': item.get('uniqueid', {}).get('tvdb'),
                    'dbid': item.get(dbid_name),
                    'title': item.get('title'),
                    'originaltitle': item.get('originaltitle'),
                    'showtitle': item.get('showtitle'),
                    'season': item.get('season'),
                    'episode': item.get('episode'),
                    'year': item.get('year'),
                    'file': item.get('file')
                }
                for item in response
            ]

        database = _get_kodi_database()

        if not database and self._logging:
            from tmdbhelper.lib.addon.logger import kodi_log
            kodi_log(f'Getting KodiDB {dbtype} FAILED!', 1)

        return database

    def _get_info(
        self, info, dbid=None, imdb_id=None, originaltitle=None, title=None, year=None,
        season=None, episode=None, fuzzy_match=False, tmdb_id=None, tvdb_id=None
    ):

        if not self.database or not info:
            return

        yearcheck = False
        index_list = find_dict_in_list(self.database, 'dbid', dbid) if dbid else []

        if not index_list and season is not None:
            index_list = find_dict_in_list(self.database, 'season', try_int(season))
        if not index_list and imdb_id:
            index_list = find_dict_in_list(self.database, 'imdb_id', imdb_id)
        if not index_list and tmdb_id:
            index_list = find_dict_in_list(self.database, 'tmdb_id', str(tmdb_id))
        if not index_list and tvdb_id:
            index_list = find_dict_in_list(self.database, 'tvdb_id', str(tvdb_id))
        if not index_list:
            yearcheck = str(year) or 'dummynull'  # Also use year if matching by title to be certain we have correct item. Dummy value for True value that will always fail comparison check.
        if not index_list and originaltitle:
            index_list = find_dict_in_list(self.database, 'originaltitle', originaltitle)
        if not index_list and title:
            index_list = find_dict_in_list(self.database, 'title', title)

        for i in index_list:
            if season is not None and episode is not None:
                if try_int(episode) == self.database[i].get('episode'):
                    return self.database[i].get(info)
            elif not yearcheck or yearcheck in str(self.database[i].get('year')):
                return self.database[i].get(info)

        if index_list and fuzzy_match and season is None and episode is None:
            """ Fuzzy Match """
            i = index_list[0]
            return self.database[i].get(info)

    def get_info(
        self, info, dbid=None, imdb_id=None, originaltitle=None, title=None, year=None,
        season=None, episode=None, fuzzy_match=False, tmdb_id=None, tvdb_id=None
    ):
        return self.cache.use(
            self._get_info, info,
            dbid=dbid,
            imdb_id=imdb_id,
            originaltitle=originaltitle,
            title=title,
            year=year,
            season=season,
            episode=episode,
            fuzzy_match=fuzzy_match,
            tmdb_id=tmdb_id,
            tvdb_id=tvdb_id,
            cache_name=f'get_info.{self._tvshowid}.{self._dbtype}',
            cache_minutes=180,
            cache_refresh=self._cache_refresh,
            cache_store_none=True)
