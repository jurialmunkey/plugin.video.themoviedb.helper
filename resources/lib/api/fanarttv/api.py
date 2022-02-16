import xbmcaddon
from resources.lib.addon.plugin import get_language
from resources.lib.addon.setutils import del_empty_keys, ITER_PROPS_MAX
from resources.lib.addon.parser import try_int
from resources.lib.files.cache import CACHE_EXTENDED
from resources.lib.api.request import RequestAPI

ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')


API_URL = 'https://webservice.fanart.tv/v3'
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
            cache_refresh=False,
            delay_write=False):
        super(FanartTV, self).__init__(
            req_api_name='FanartTV',
            req_api_url=API_URL,
            req_api_key=u'api_key={}'.format(api_key),
            delay_write=delay_write)
        self.req_api_key = u'api_key={0}'.format(api_key) if api_key else self.req_api_key
        self.req_api_key = u'{0}&client_key={1}'.format(self.req_api_key, client_key) if client_key else self.req_api_key
        self.language = language[:2] if language else 'en'
        self.cache_only = cache_only
        self.cache_refresh = cache_refresh
        self.quick_request = {'movies': {}, 'tv': {}}
        self.req_strip.append(('&client_key={}'.format(client_key), ''))

    def get_all_artwork(self, ftv_id, ftv_type, season=None, artlist_type=None):
        """
        ftv_type can be 'movies' 'tv'
        ftv_id is tmdb_id|imdb_id for movies and tvdb_id for tv
        """
        def get_artwork_type(art_type, get_lang=True):
            if not art_type:
                return
            data = request.get(art_type) or []
            if not get_lang:
                data = [i for i in data if i.get('lang') in ['00', None]]
            if season is not None:
                data = [i for i in data if try_int(season) == try_int(i.get('season'))]
            return data

        def get_best_artwork(art_type, get_lang=True):
            language = self.language if get_lang else '00'
            response = get_artwork_type(art_type, get_lang)
            try:
                return next((i for i in response if i.get('lang') == language or (language == '00' and not i.get('lang')))).get('url', '')
            except StopIteration:
                pass
            response = [i for i in response if i.get('lang') in ['en', '00', None]]
            if not response:
                return
            response.sort(key=lambda i: int(i.get('likes', 0)), reverse=True)
            return response[0].get('url', '')

        def get_artwork(art_type, get_list=False, get_lang=True):
            func = get_best_artwork if not get_list else get_artwork_type
            for i in artwork_types.get(art_type, []):
                data = func(i, get_lang)
                if data:
                    return data

        # __main__
        if not ftv_type or not ftv_id:
            return {}
        request = self.quick_request[ftv_type].get(ftv_id)
        if not request:
            request = self.quick_request[ftv_type][ftv_id] = self.get_request(
                ftv_type, ftv_id,
                cache_force=7,  # Force dummy request caching to prevent rerequesting 404s
                cache_fallback={'dummy': None},
                cache_days=CACHE_EXTENDED,
                cache_only=self.cache_only,
                cache_refresh=self.cache_refresh)
        if not request or 'dummy' in request:
            return {}
        artwork_types = ARTWORK_TYPES.get(ftv_type if season is None else 'season', {})
        if artlist_type:
            return get_artwork(artlist_type, get_list=True, get_lang=artlist_type not in NO_LANGUAGE)
        artwork_data = del_empty_keys({i: get_artwork(i, get_lang=i not in NO_LANGUAGE) for i in artwork_types})
        return add_extra_art(get_artwork('fanart', get_list=True), artwork_data)
