import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.addon.plugin import get_language
from resources.lib.addon.setutils import del_empty_keys, ITER_PROPS_MAX
from resources.lib.addon.decorators import busy_dialog
from resources.lib.addon.parser import try_int
from resources.lib.addon.constants import ARTWORK_BLACKLIST
from resources.lib.files.cache import CACHE_EXTENDED
from resources.lib.items.listitem import ListItem
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
        cache_name = u'FanartTV.allart_v2.{}.{}.{}'.format(ftv_id, ftv_type, season)
        all_artwork = None if self.cache_refresh else self._cache.get_cache(cache_name)
        if all_artwork:
            return all_artwork
        request = self.get_artwork_request(ftv_id, ftv_type)
        if not request:
            return  # Check we can get the request first so we don't re-ask eight times if it 404s
        artwork_types = ARTWORK_TYPES.get(ftv_type if season is None else 'season', {})
        all_artwork = del_empty_keys({
            i: self.get_artwork(ftv_id, ftv_type, i, request=request, get_lang=i not in NO_LANGUAGE, season=season)
            for i in artwork_types})
        return self._cache.set_cache(
            add_extra_art(self.get_artwork(ftv_id, ftv_type, 'fanart', get_list=True, request=request), all_artwork),
            cache_name=cache_name)

    def refresh_all_artwork(self, ftv_id, ftv_type, ok_dialog=True, container_refresh=True, season=None):
        self.cache_refresh = True
        with busy_dialog():
            artwork = self.get_all_artwork(ftv_id, ftv_type, season)
        if ok_dialog and not artwork:
            xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))
        if ok_dialog and artwork:
            xbmcgui.Dialog().ok('FanartTV', ADDON.getLocalizedString(32218).format(
                ftv_type, ftv_id, ', '.join([k.capitalize() for k, v in artwork.items() if v])))
        if artwork and container_refresh:
            xbmc.executebuiltin('Container.Refresh')
            xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')
        return artwork

    def get_artwork(self, ftv_id, ftv_type, artwork_type, get_list=False, get_lang=True, request=None, season=None):
        artwork_types = ARTWORK_TYPES.get(ftv_type if season is None else 'season', {}).get(artwork_type) or []
        func = self.get_best_artwork if not get_list else self.get_artwork_type
        for i in artwork_types:
            artwork = func(ftv_id, ftv_type, i, get_lang, request=request, season=season)
            if artwork:
                return artwork

    def select_artwork(self, ftv_id, ftv_type, container_refresh=True, blacklist=[], season=None):
        if ftv_type not in ['movies', 'tv']:
            return
        with busy_dialog():
            artwork = self.get_artwork_request(ftv_id, ftv_type)
        if not artwork:
            return xbmcgui.Dialog().notification('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))

        # Choose Type
        artwork_types = [i for i in ARTWORK_TYPES.get(ftv_type if season is None else 'season') if i not in blacklist]  # Remove types that we previously looked for
        choice = xbmcgui.Dialog().select(xbmc.getLocalizedString(13511), artwork_types)
        if choice == -1:
            return

        # Get artwork of user's choosing
        artwork_type = artwork_types[choice]
        get_lang = artwork_type not in NO_LANGUAGE
        artwork_items = self.get_artwork(ftv_id, ftv_type, artwork_type, get_list=True, get_lang=get_lang, season=season)

        # If there was not artwork of that type found then blacklist it before re-prompting
        if not artwork_items:
            xbmcgui.Dialog().notification('FanartTV', ADDON.getLocalizedString(32217).format(ftv_type, ftv_id))
            blacklist.append(artwork_types[choice])
            return self.select_artwork(ftv_id, ftv_type, container_refresh, blacklist, season=season)

        # Choose artwork from options
        items = [
            ListItem(
                label=i.get('url'),
                label2=ADDON.getLocalizedString(32219).format(i.get('lang', ''), i.get('likes', 0), i.get('id', '')),
                art={'thumb': i.get('url')}).get_listitem() for i in artwork_items if i.get('url')]
        choice = xbmcgui.Dialog().select(xbmc.getLocalizedString(13511), items, useDetails=True)
        if choice == -1:  # If user hits back go back to main menu rather than exit completely
            return self.select_artwork(ftv_id, ftv_type, container_refresh, blacklist, season=season)

        success = artwork_items[choice].get('url')
        if not success:
            return

        # Cache our artwork forever since it was selected manually
        all_art = self.get_all_artwork(ftv_id, ftv_type, season)
        if not all_art:
            return
        all_art[artwork_type] = success
        self._cache.set_cache(all_art, cache_name=u'FanartTV.allart_v2.{}.{}.{}'.format(ftv_id, ftv_type, season), cache_days=10000)

        if container_refresh:
            xbmc.executebuiltin('Container.Refresh')
            xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')

    def manage_artwork(self, ftv_id=None, ftv_type=None, season=None):
        if not ftv_id or not ftv_type:
            return
        choice = xbmcgui.Dialog().contextmenu([
            ADDON.getLocalizedString(32220),
            ADDON.getLocalizedString(32221)])
        if choice == -1:
            return
        if choice == 0:
            blacklist = ARTWORK_BLACKLIST[ADDON.getSettingInt('artwork_quality')]
            return self.select_artwork(ftv_id=ftv_id, ftv_type=ftv_type, season=season, blacklist=blacklist)
        if choice == 1:
            return self.refresh_all_artwork(ftv_id=ftv_id, ftv_type=ftv_type, season=season)
