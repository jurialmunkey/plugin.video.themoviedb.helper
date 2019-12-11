from resources.lib.requestapi import RequestAPI


class FanartTV(RequestAPI):
    def __init__(self, api_key=None, client_key=None, language=None, cache_long=None, cache_short=None):
        super(FanartTV, self).__init__(
            cache_short=cache_short, cache_long=cache_long,
            req_api_name='FanartTV', req_api_url='http://webservice.fanart.tv/v3', req_wait_time=0,
            req_api_key='?api_key=fcca59bee130b70db37ee43e63f8d6c1')
        self.req_api_key = '?api_key={0}'.format(api_key) if api_key else self.req_api_key
        self.req_api_key = '{0}&client_key={1}'.format(self.req_api_key, client_key) if client_key else self.req_api_key
        self.language = language[:2] if language else 'en'
        self.response, self.ftvtype, self.ftvid = None, None, None

    def get_artwork_request(self, ftvid=None, ftvtype=None):
        """
        ftvtype can be 'movies' 'tv'
        ftvid is tmdb_id|imdb_id for movies and tvdb_id for tv
        """
        if not ftvtype or not ftvid:
            return
        self.response = self.get_request_lc(ftvtype, ftvid)
        self.ftvtype = ftvtype
        self.ftvid = ftvid
        return self.response

    def get_artwork_list(self, ftvid=None, ftvtype=None, artwork=None):
        if not artwork:
            return []
        if self.response:
            if (self.ftvtype != ftvtype or self.ftvid != ftvid) and not self.get_artwork_request(ftvtype, ftvid):
                return []
        elif not ftvtype or not ftvid or not self.get_artwork_request(ftvtype, ftvid):
            return []
        return self.response.get(artwork, [])

    def get_artwork_best(self, ftvid=None, ftvtype=None, artwork=None):
        best_like = -1
        best_item = None
        for i in self.get_artwork_list(ftvtype, ftvid, artwork):
            if i.get('lang', '') == self.language:
                return i.get('url', '')
            elif i.get('likes', 0) > best_like:
                best_item = i.get('url', '')
                best_like = i.get('likes', 0)
        return best_item

    def get_movie_clearart(self, ftvid=None):
        artwork = self.get_artwork_best(ftvid, 'movies', 'hdmovieclearart')
        return artwork or self.get_artwork_best(ftvid, 'movies', 'movieclearart')

    def get_movie_clearlogo(self, ftvid=None):
        artwork = self.get_artwork_best(ftvid, 'movies', 'hdmovielogo')
        return artwork or self.get_artwork_best(ftvid, 'movies', 'movielogo')

    def get_movie_poster(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'movies', 'movieposter')

    def get_movie_fanart(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'movies', 'moviebackground')

    def get_movie_landscape(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'movies', 'moviethumb')

    def get_movie_banner(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'movies', 'moviebanner')

    def get_tvshow_clearart(self, ftvid=None):
        artwork = self.get_artwork_best(ftvid, 'tv', 'hdclearart')
        return artwork or self.get_artwork_best(ftvid, 'tv', 'clearart')

    def get_tvshow_clearlogo(self, ftvid=None):
        artwork = self.get_artwork_best(ftvid, 'tv', 'hdtvlogo')
        return artwork or self.get_artwork_best(ftvid, 'tv', 'clearlogo')

    def get_tvshow_banner(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'tv', 'tvbanner')

    def get_tvshow_landscape(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'tv', 'tvthumb')

    def get_tvshow_fanart(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'tv', 'showbackground')

    def get_tvshow_characterart(self, ftvid=None):
        return self.get_artwork_best(ftvid, 'tv', 'characterart')
