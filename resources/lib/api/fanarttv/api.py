import xbmcaddon
from resources.lib.addon.plugin import get_language
from resources.lib.addon.setutils import del_empty_keys, ITER_PROPS_MAX
from resources.lib.addon.parser import try_int
from resources.lib.files.cache import CACHE_EXTENDED
from resources.lib.api.request import RequestAPI

ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')


API_URL = 'http://webservice.fanart.tv/v3'
NO_LANGUAGE = ['keyart', 'fanart']
ARTWORK_TYPES = {
    'movies': {
        'clearart': ['hdmovieclearart', 'movieclearart'],
        'clearlogo': ['hdmovielogo', 'movielogo'],
        'discart': ['moviedisc'],
        'poster': ['movieposter'],
        'fanart': ['moviebackground'],
        'landscape': ['moviethumb'],
        'banner': ['moviebanner'],
        'keyart': ['movieposter']},
    'tv': {
        'clearart': ['hdclearart', 'clearart'],
        'clearlogo': ['hdtvlogo', 'clearlogo'],
        'characterart': ['characterart'],
        'poster': ['tvposter'],
        'fanart': ['showbackground'],
        'landscape': ['tvthumb'],
        'banner': ['tvbanner']},
    'season': {
        'poster': ['seasonposter', 'tvposter'],
        'fanart': ['showbackground'],
        'landscape': ['seasonthumb', 'tvthumb'],
        'banner': ['seasonbanner', 'tvbanner']}
}


def add_extra_art(source, output={}):
    if not source:
        return output
    output.update({u'fanart{}'.format(x): i['url'] for x, i in enumerate(source, 1) if i.get('url') and x <= ITER_PROPS_MAX})
    return output


class FanartTV(RequestAPI):
    def __init__(
            self,
            api_key='fcca59bee130b70db37ee43e63f8d6c1',
            client_key=ADDON.getSettingString('fanarttv_clientkey'),
            language=get_language(),
            cache_only=False,
            cache_refresh=False):
        super(FanartTV, self).__init__(
            req_api_name='FanartTV',
            req_api_url=API_URL,
            req_api_key=u'api_key={}'.format(api_key))
        self.req_api_key = u'api_key={0}'.format(api_key) if api_key else self.req_api_key
        self.req_api_key = u'{0}&client_key={1}'.format(self.req_api_key, client_key) if client_key else self.req_api_key
        self.language = language[:2] if language else 'en'
        self.cache_only = cache_only
        self.cache_refresh = cache_refresh
        self.quick_request = {'movies': {}, 'tv': {}}
        self.req_strip.append(('&client_key={}'.format(client_key), ''))

    def get_artwork_request(self, ftv_id, ftv_type):
        """
        ftv_type can be 'movies' 'tv'
        ftv_id is tmdb_id|imdb_id for movies and tvdb_id for tv
        """
        if not ftv_type or not ftv_id:
            return
        request = self.quick_request[ftv_type].get(ftv_id)
        if not request:
            self.quick_request[ftv_type][ftv_id] = request = self.get_request(
                ftv_type, ftv_id,
                cache_force=7,  # Force the cache to save a dummy dict for 7 days so that we don't bother requesting 404s multiple times
                cache_fallback={'dummy': None},
                cache_days=CACHE_EXTENDED,
                cache_only=self.cache_only,
                cache_refresh=self.cache_refresh)
        if request and 'dummy' not in request:
            return request

    def get_artwork_type(self, ftv_id, ftv_type, artwork_type, get_lang=True, request=None, **kwargs):
        if not artwork_type:
            return
        response = request or self.get_artwork_request(ftv_id, ftv_type)
        if not response:
            return
        response = response.get(artwork_type) or []
        return response if get_lang else [i for i in response if not i.get('lang') or i['lang'] == '00']

    def get_best_artwork(self, ftv_id, ftv_type, artwork_type, get_lang=True, request=None, season=None, **kwargs):
        language = self.language if get_lang else '00'
        artwork = self.get_artwork_type(ftv_id, ftv_type, artwork_type, get_lang, request=request)
        best_like = -1
        best_item = None
        for i in artwork:
            if season is not None and try_int(season) != try_int(i.get('season')):
                continue
            i_lang = i.get('lang')
            if i_lang == language or (language == '00' and not i_lang):
                return i.get('url', '')
            i_like = try_int(i.get('likes', 0))
            if i_lang in ['en', '00', None] and i_like > best_like:
                best_item = i.get('url', '')
                best_like = i_like
        return best_item

    def get_all_artwork(self, ftv_id, ftv_type, season=None):
        request = self.get_artwork_request(ftv_id, ftv_type)
        if not request:
            return  # Check we can get the request first so we don't re-ask eight times if it 404s
        artwork_types = ARTWORK_TYPES.get(ftv_type if season is None else 'season', {})
        all_artwork = del_empty_keys({
            i: self.get_artwork(ftv_id, ftv_type, i, request=request, get_lang=i not in NO_LANGUAGE, season=season)
            for i in artwork_types})
        return add_extra_art(self.get_artwork(ftv_id, ftv_type, 'fanart', get_list=True, request=request), all_artwork)

    def get_artwork(self, ftv_id, ftv_type, artwork_type, get_list=False, get_lang=True, request=None, season=None):
        artwork_types = ARTWORK_TYPES.get(ftv_type if season is None else 'season', {}).get(artwork_type) or []
        func = self.get_best_artwork if not get_list else self.get_artwork_type
        for i in artwork_types:
            artwork = func(ftv_id, ftv_type, i, get_lang, request=request, season=season)
            if artwork:
                return artwork
