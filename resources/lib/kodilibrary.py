import xbmc
import json
import resources.lib.utils as utils


class KodiLibrary(object):
    def __init__(self, dbtype=None, tvshowid=None):
        if not dbtype:
            return
        if dbtype == "movie":
            method = "VideoLibrary.GetMovies"
            params = {"properties": ["title", "imdbnumber", "originaltitle", "year", "file"]}
        if dbtype == "tvshow":
            method = "VideoLibrary.GetTVShows"
            params = {"properties": ["title", "imdbnumber", "originaltitle", "year"]}
        if dbtype == "episode":
            method = "VideoLibrary.GetEpisodes"
            params = {
                "tvshowid": tvshowid,
                "properties": ["title", "showtitle", "season", "episode", "file"]}
        query = {
            "jsonrpc": "2.0",
            "params": params,
            "method": method,
            "id": 1}
        response = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        dbid_name = '{0}id'.format(dbtype)
        key_to_get = '{0}s'.format(dbtype)
        self.database = [{
            'imdb_id': item.get('imdbnumber'),
            'dbid': item.get(dbid_name),
            'title': item.get('title'),
            'originaltitle': item.get('originaltitle'),
            'showtitle': item.get('showtitle'),
            'season': item.get('season'),
            'episode': item.get('episode'),
            'year': item.get('year'),
            'file': item.get('file')}
            for item in response.get('result', {}).get(key_to_get, [])]

    def get_info(self, info, dbid=None, imdb_id=None, originaltitle=None, title=None, year=None, season=None, episode=None):
        if not self.database or not info:
            return
        index_list = utils.find_dict_in_list(self.database, 'dbid', dbid) if dbid else []
        if not index_list and season:
            index_list = utils.find_dict_in_list(self.database, 'season', utils.try_parse_int(season))
        if not index_list and imdb_id:
            index_list = utils.find_dict_in_list(self.database, 'imdb_id', imdb_id)
        if not index_list and originaltitle:
            index_list = utils.find_dict_in_list(self.database, 'originaltitle', originaltitle)
        if not index_list and title:
            index_list = utils.find_dict_in_list(self.database, 'title', title)
        for i in index_list:
            if season and episode:
                if utils.try_parse_int(episode) == self.database[i].get('episode'):
                    return self.database[i].get(info)
            elif not year or year in str(self.database[i].get('year')):
                return self.database[i].get(info)
