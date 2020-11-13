# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
from resources.lib.kodi.update import add_userlist, monitor_userlist, library_autoupdate
from resources.lib.files.downloader import Downloader
from resources.lib.addon.window import get_property
from resources.lib.container.basedir import get_basedir_details
from resources.lib.fanarttv.api import FanartTV
from resources.lib.tmdb.api import TMDb
from resources.lib.trakt.api import TraktAPI, get_sort_methods
from resources.lib.addon.plugin import ADDON, reconfigure_legacy_params, viewitems, kodi_log, format_folderpath, convert_type
from resources.lib.kodi.rpc import get_jsonrpc
from resources.lib.script.sync import SyncItem
from resources.lib.addon.decorators import busy_dialog
from resources.lib.addon.parser import encode_url, try_encode, try_decode
from resources.lib.window.manager import WindowManager
from resources.lib.player.players import Players
from resources.lib.player.configure import configure_players
from resources.lib.monitor.images import ImageFunctions


WM_PARAMS = ['add_path', 'add_query', 'close_dialog', 'reset_path', 'call_id', 'call_path', 'call_update']


# Get TMDb ID decorator
def get_tmdb_id(func):
    def wrapper(*args, **kwargs):
        with busy_dialog():
            if not kwargs.get('tmdb_id'):
                kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)
        return func(*args, **kwargs)
    return wrapper


def map_kwargs(mapping={}):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in viewitems(mapping):
                if k in kwargs:
                    kwargs[v] = kwargs.pop(k, None)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def is_in_kwargs(mapping={}):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in viewitems(mapping):
                if kwargs.get(k) not in v:
                    return
            return func(*args, **kwargs)
        return wrapper
    return decorator


def play_media(**kwargs):
    with busy_dialog():
        kodi_log(['lib.script.router - attempting to play\n', kwargs.get('play_media')], 1)
        xbmc.executebuiltin(try_encode(u'PlayMedia({})'.format(kwargs.get('play_media'))))


def run_plugin(**kwargs):
    with busy_dialog():
        kodi_log(['lib.script.router - attempting to play\n', kwargs.get('run_plugin')], 1)
        xbmc.executebuiltin(try_encode(u'RunPlugin({})'.format(kwargs.get('run_plugin'))))


@map_kwargs({'play': 'tmdb_type'})
@get_tmdb_id
def play_external(**kwargs):
    kodi_log(['lib.script.router - attempting to play\n', kwargs], 1)
    Players(**kwargs).play()


# def add_to_queue(episodes, clear_playlist=False, play_next=False):
#     if not episodes:
#         return
#     playlist = xbmc.PlayList(1)
#     if clear_playlist:
#         playlist.clear()
#     for i in episodes:
#         li = ListItem(**i)
#         li.set_params_reroute()
#         playlist.add(li.get_url(), li.get_listitem())
#     if play_next:
#         xbmc.Player().play(playlist)


# def play_season(**kwargs):
#     with busy_dialog():
#         if not kwargs.get('tmdb_id'):
#             kwargs['tmdb_type'] = 'tv'
#             kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)
#         if not kwargs['tmdb_id']:
#             return
#         add_to_queue(
#             TMDb().get_episode_list(tmdb_id=kwargs['tmdb_id'], season=kwargs['play_season']),
#             clear_playlist=True, play_next=True)


def split_value(split_value, separator=None, **kwargs):
    split_value = split_value or ''
    for x, i in enumerate(split_value.split(separator or ' / ')):
        name = '{}.{}'.format(kwargs.get('property') or 'TMDbHelper.Split', x)
        get_property(name, set_property=i, prefix=-1)


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_trakt(**kwargs):
    SyncItem(
        trakt_type=convert_type(kwargs['tmdb_type'], 'trakt', season=kwargs.get('season'), episode=kwargs.get('episode')),
        unique_id=kwargs['tmdb_id'],
        season=kwargs.get('season'),
        episode=kwargs.get('episode'),
        id_type='tmdb').sync()


def manage_artwork(ftv_id=None, ftv_type=None, **kwargs):
    FanartTV().manage_artwork(ftv_id, ftv_type)


def related_lists(tmdb_id=None, tmdb_type=None, season=None, episode=None, container_update=True, include_play=False, **kwargs):
    if not tmdb_id or not tmdb_type:
        return
    items = get_basedir_details(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, include_play=include_play)
    if not items or len(items) <= 1:
        return
    choice = xbmcgui.Dialog().contextmenu([i.get('label') for i in items])
    if choice == -1:
        return
    item = items[choice]
    params = item.get('params')
    if not params:
        return
    item['params']['tmdb_id'] = tmdb_id
    item['params']['tmdb_type'] = tmdb_type
    if not container_update:
        return item
    path = format_folderpath(
        path=encode_url(path=item.get('path'), **item.get('params')),
        info=item['params']['info'], play='RunPlugin',  # Use RunPlugin to avoid window manager info dialog crash with Browse method
        content='pictures' if item['params']['info'] in ['posters', 'fanart'] else 'videos')
    xbmc.executebuiltin(try_encode(path))


def update_players():
    players_url = ADDON.getSettingString('players_url')
    players_url = xbmcgui.Dialog().input(ADDON.getLocalizedString(32313), defaultt=players_url)
    if not xbmcgui.Dialog().yesno(
            ADDON.getLocalizedString(32032),
            ADDON.getLocalizedString(32314).format(players_url)):
        return
    ADDON.setSettingString('players_url', players_url)
    downloader = Downloader(
        extract_to='special://profile/addon_data/plugin.video.themoviedb.helper/players',
        download_url=players_url)
    downloader.get_extracted_zip()


def refresh_details(tmdb_id=None, tmdb_type=None, season=None, episode=None, **kwargs):
    if not tmdb_id or not tmdb_type:
        return
    with busy_dialog():
        details = TMDb().get_details(tmdb_type, tmdb_id, season, episode, cache_refresh=True)
    if details:
        xbmcgui.Dialog().ok('TMDbHelper', ADDON.getLocalizedString(32234).format(tmdb_type, tmdb_id))
        xbmc.executebuiltin('Container.Refresh')
        xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')


def kodi_setting(kodi_setting, **kwargs):
    method = "Settings.GetSettingValue"
    params = {"setting": kodi_setting}
    response = get_jsonrpc(method, params)
    get_property(
        name=kwargs.get('property') or 'TMDbHelper.KodiSetting',
        set_property=u'{}'.format(response.get('result', {}).get('value', '')))


def user_list(user_list, user_slug=None, **kwargs):
    user_slug = user_slug or 'me'
    if not user_slug or not user_list:
        return
    add_userlist(user_slug=user_slug, list_slug=user_list, confirm=True, allow_update=True, busy_spinner=True)


def like_list(like_list, user_slug=None, delete=False, **kwargs):
    user_slug = user_slug or 'me'
    if not user_slug or not like_list:
        return
    TraktAPI().like_userlist(user_slug=user_slug, list_slug=like_list, confirmation=True, delete=delete)
    if not delete:
        return
    xbmc.executebuiltin('Container.Refresh')
    xbmc.executebuiltin('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)')


def set_defaultplayer(**kwargs):
    tmdb_type = kwargs.get('set_defaultplayer')
    setting_name = 'default_player_movies' if tmdb_type == 'movie' else 'default_player_episodes'
    default_player = Players(tmdb_type).select_player(detailed=True, clear_player=True)
    if not default_player:
        return
    if not default_player.get('file') or not default_player.get('mode'):
        return ADDON.setSettingString(setting_name, '')
    ADDON.setSettingString(setting_name, u'{} {}'.format(default_player['file'], default_player['mode']))


def blur_image(blur_image=None, **kwargs):
    blur_img = ImageFunctions(method='blur', artwork=blur_image)
    blur_img.setName('blur_img')
    blur_img.start()


def image_colors(image_colors=None, **kwargs):
    image_colors = ImageFunctions(method='colors', artwork=image_colors)
    image_colors.setName('image_colors')
    image_colors.start()


def library_update(**kwargs):
    library_autoupdate(
        list_slugs=kwargs.get('list_slug', None),
        user_slugs=kwargs.get('user_slug', None),
        busy_spinner=True if kwargs.get('busy_dialog', False) else False,
        force=kwargs.get('force', False))


def log_request(**kwargs):
    request = None
    if kwargs.get('log_request') == 'trakt':
        request = TraktAPI().get_response_json(kwargs.get('url'))
    elif kwargs.get('log_request') == 'tmdb':
        request = TMDb().get_response_json(kwargs.get('url'))
    kodi_log([kwargs.get('log_request'), '\n', kwargs.get('url'), '\n', request], 1)


def sort_list(**kwargs):
    sort_methods = get_sort_methods()
    x = xbmcgui.Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in viewitems(sort_methods[x]['params']):
        kwargs[k] = v
    xbmc.executebuiltin(try_encode(format_folderpath(encode_url(**kwargs))))


class Script(object):
    def get_params(self):
        params = {}
        for arg in sys.argv:
            if arg == 'script.py':
                pass
            elif '=' in arg:
                arg_split = arg.split('=', 1)
                if arg_split[0] and arg_split[1]:
                    key, value = try_decode(arg_split[0]), try_decode(arg_split[1])
                    value = value.strip('\'').strip('\"')
                    params.setdefault(key, value)
            else:
                params.setdefault(arg, True)
        return params

    def router(self):
        self.params = self.get_params()
        if not self.params:
            return
        self.params = reconfigure_legacy_params(**self.params)
        if self.params.get('authenticate_trakt'):
            return TraktAPI(force=True)
        if self.params.get('revoke_trakt'):
            return TraktAPI().logout()
        if self.params.get('split_value'):
            return split_value(**self.params)
        if self.params.get('kodi_setting'):
            return kodi_setting(**self.params)
        if self.params.get('sync_trakt'):
            return sync_trakt(**self.params)
        if self.params.get('manage_artwork'):
            return manage_artwork(**self.params)
        if self.params.get('refresh_details'):
            return refresh_details(**self.params)
        if self.params.get('related_lists'):
            return related_lists(**self.params)
        if self.params.get('user_list'):
            return user_list(**self.params)
        if self.params.get('like_list'):
            return like_list(**self.params)
        if self.params.get('blur_image'):
            return blur_image(**self.params)
        if self.params.get('image_colors'):
            return image_colors(**self.params)
        if self.params.get('monitor_userlist'):
            return monitor_userlist()
        if self.params.get('update_players'):
            return update_players()
        if self.params.get('set_defaultplayer'):
            return set_defaultplayer(**self.params)
        if self.params.get('configure_players'):
            return configure_players(**self.params)
        if self.params.get('library_autoupdate'):
            return library_update(**self.params)
        if any(x in WM_PARAMS for x in self.params):
            return WindowManager(**self.params).router()
        # if self.params.get('play_season'):
        #     return play_season(**self.params)
        if self.params.get('play_media'):
            return play_media(**self.params)
        if self.params.get('run_plugin'):
            return run_plugin(**self.params)
        if self.params.get('log_request'):
            return log_request(**self.params)
        if self.params.get('play'):
            return play_external(**self.params)
        if self.params.get('restart_service'):
            # Only do the import here because this function only for debugging purposes
            from resources.lib.monitor.service import restart_service_monitor
            return restart_service_monitor()
