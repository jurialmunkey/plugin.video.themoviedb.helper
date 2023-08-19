from xbmc import Monitor
from tmdbhelper.lib.addon.logger import kodi_log
from jurialmunkey.parser import try_int, find_dict_in_list
from tmdbhelper.lib.api.kodi.mapping import ItemMapper
from tmdbhelper.lib.files.mcache import MemoryCache
from tmdbhelper.lib.addon.thread import use_thread_lock
import jurialmunkey.jsnrpc as jurialmunkey_jsnrpc

""" Lazyimports
from json import dumps, loads
from tmdbhelper.lib.files.bcache import BasicCache
from xbmcvfs import Stat
"""


get_library = jurialmunkey_jsnrpc.get_library
get_num_credits = jurialmunkey_jsnrpc.get_num_credits
set_tags = jurialmunkey_jsnrpc.set_tags
set_watched = jurialmunkey_jsnrpc.set_watched
set_playprogress = jurialmunkey_jsnrpc.set_playprogress
get_directory = jurialmunkey_jsnrpc.get_directory


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


def get_person_stats(person):
    infoproperties = {}
    infoproperties['numitems.dbid.movies'] = get_num_credits('movie', person)
    infoproperties['numitems.dbid.tvshows'] = get_num_credits('tvshow', person)
    infoproperties['numitems.dbid.episodes'] = get_num_credits('episode', person)
    infoproperties['numitems.dbid.total'] = (
        try_int(infoproperties.get('numitems.dbid.movies'))
        + try_int(infoproperties.get('numitems.dbid.tvshows'))
        + try_int(infoproperties.get('numitems.dbid.episodes')))
    return infoproperties


def get_item_details(dbid=None, method=None, key=None, properties=None):
    if not dbid or not method or not key or not properties:
        return {}
    params = {
        f'{key}id': try_int(dbid),
        "properties": properties}
    try:
        details = get_jsonrpc(method, params)
        details = details['result'][f'{key}details']
        details['dbid'] = dbid
        return ItemMapper(key=key).get_info(details)
    except (AttributeError, KeyError):
        return {}


def get_movie_details(dbid=None):
    properties = [
        "title", "genre", "year", "rating", "director", "trailer", "tagline", "plot", "plotoutline", "originaltitle",
        "lastplayed", "playcount", "writer", "studio", "mpaa", "cast", "country", "imdbnumber", "runtime", "set",
        "showlink", "streamdetails", "top250", "votes", "fanart", "thumbnail", "file", "sorttitle", "resume", "setid",
        "dateadded", "tag", "art", "userrating", "ratings", "premiered", "uniqueid"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetMovieDetails", key="movie", properties=properties)


def get_tvshow_details(dbid=None):
    properties = [
        "title", "genre", "year", "rating", "plot", "studio", "mpaa", "cast", "playcount", "episode", "imdbnumber",
        "premiered", "votes", "lastplayed", "fanart", "thumbnail", "file", "originaltitle", "sorttitle", "episodeguide",
        "season", "watchedepisodes", "dateadded", "tag", "art", "userrating", "ratings", "runtime", "uniqueid"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetTVShowDetails", key="tvshow", properties=properties)


def get_season_details(dbid=None):
    properties = [
        "season", "showtitle", "playcount", "episode", "fanart", "thumbnail", "tvshowid", "watchedepisodes",
        "art", "userrating", "title"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetSeasonDetails", key="season", properties=properties)


def get_episode_details(dbid=None):
    properties = [
        "title", "plot", "votes", "rating", "writer", "firstaired", "playcount", "runtime", "director", "productioncode",
        "season", "episode", "originaltitle", "showtitle", "cast", "streamdetails", "lastplayed", "fanart", "thumbnail",
        "file", "resume", "tvshowid", "dateadded", "uniqueid", "art", "specialsortseason", "specialsortepisode", "userrating",
        "seasonid", "ratings"]
    return get_item_details(dbid=dbid, method="VideoLibrary.GetEpisodeDetails", key="episode", properties=properties)


THREAD_LOCK = 'TMDbHelper.KodiLibrary.ThreadLock'


class KodiLibrary(object):
    def __init__(self, dbtype=None, tvshowid=None, attempt_reconnect=False, logging=True, cache_refresh=False):
        self.dbtype = dbtype
        self._cache = MemoryCache(name='KodiLibrary_{dbtype}_{tvshowid}')
        self._get_database(dbtype, tvshowid, attempt_reconnect, logging, cache_refresh)

    @use_thread_lock(THREAD_LOCK)
    def _get_database(self, dbtype, tvshowid=None, attempt_reconnect=False, logging=True, cache_refresh=False):

        def _get_db():
            if dbtype == 'both':
                movies = self._cache.use(
                    self.get_database, 'movie', None, attempt_reconnect,
                    cache_name='database', cache_minutes=180, cache_refresh=cache_refresh) or []
                tvshows = self._cache.use(
                    self.get_database, 'tvshow', None, attempt_reconnect,
                    cache_name='database', cache_minutes=180, cache_refresh=cache_refresh) or []
                return movies + tvshows
            return self._cache.use(
                self.get_database, dbtype, tvshowid, attempt_reconnect,
                cache_name='database', cache_minutes=180, cache_refresh=cache_refresh)

        self.database = _get_db()

        return self.database

    def get_database(self, dbtype, tvshowid=None, attempt_reconnect=False, logging=True):
        retries = 5 if attempt_reconnect else 1
        while not Monitor().abortRequested() and retries > 0:
            database = self._get_kodi_db(dbtype, tvshowid)
            if database:
                return database
            Monitor().waitForAbort(1)
            retries -= 1
        if logging:
            kodi_log(f'Getting KodiDB {dbtype} FAILED!', 1)

    def _get_kodi_db(self, dbtype=None, tvshowid=None):
        if not dbtype:
            return
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
        return [{
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
            'file': item.get('file')}
            for item in response]

    def get_info(
            self, info, dbid=None, imdb_id=None, originaltitle=None, title=None, year=None, season=None,
            episode=None, fuzzy_match=False, tmdb_id=None, tvdb_id=None):
        if not self.database or not info:
            return
        yearcheck = False
        index_list = find_dict_in_list(self.database, 'dbid', dbid) if dbid else []
        if not index_list and season:
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
            if season and episode:
                if try_int(episode) == self.database[i].get('episode'):
                    return self.database[i].get(info)
            elif not yearcheck or yearcheck in str(self.database[i].get('year')):
                return self.database[i].get(info)
        if index_list and fuzzy_match and not season and not episode:
            """ Fuzzy Match """
            i = index_list[0]
            return self.database[i].get(info)
