# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
def map_kwargs(mapping={}):
    """ Decorator to remap kwargs key names """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in mapping.items():
                if k in kwargs:
                    kwargs[v] = kwargs.pop(k, None)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def is_in_kwargs(mapping={}):
    """ Decorator to check that kwargs values match allowlist before running
    Accepts a dictionary of {kwarg: [allowlist]} key value pairs
    Decorated method is not run if kwargs.get(kwarg) not in [allowlist]
    Optionally can use {kwarg: True} to check kwarg exists and has any value
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for k, v in mapping.items():
                if v is True:
                    if kwargs.get(k) is None:
                        return
                else:
                    if kwargs.get(k) not in v:
                        return
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_tmdb_id(func):
    """ Decorator to get tmdb_id if not in kwargs """
    def wrapper(*args, **kwargs):
        from tmdbhelper.lib.addon.dialog import BusyDialog
        from tmdbhelper.lib.api.tmdb.api import TMDb
        with BusyDialog():
            if not kwargs.get('tmdb_id'):
                kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)
                if not kwargs['tmdb_id']:
                    return
        return func(*args, **kwargs)
    return wrapper


def choose_tmdb_id(func):
    """ Decorator to get tmdb_id if not in kwargs """
    def wrapper(*args, **kwargs):
        if kwargs.get('tmdb_id'):
            return func(*args, **kwargs)

        from xbmcgui import Dialog, ListItem
        from tmdbhelper.lib.addon.dialog import BusyDialog
        from tmdbhelper.lib.api.tmdb.api import TMDb
        from tmdbhelper.lib.api.tmdb.mapping import get_imagepath_poster

        if kwargs.get('query'):
            with BusyDialog():
                response = TMDb().get_request_sc('search', kwargs['tmdb_type'], query=kwargs['query'])
            if not response or not response.get('results'):
                return

            items = []
            for i in response['results']:
                li = ListItem(
                    i.get('title') or i.get('name'),
                    i.get('release_date') or i.get('first_air_date'))
                li.setArt({'icon': get_imagepath_poster(i.get('poster_path'))})
                items.append(li)

            x = Dialog().select(kwargs['query'], items, useDetails=True)
            if x == -1:
                return
            kwargs['tmdb_id'] = response['results'][x].get('id')

        else:
            with BusyDialog():
                kwargs['tmdb_id'] = TMDb().get_tmdb_id(**kwargs)

        if not kwargs['tmdb_id']:
            return

        return func(*args, **kwargs)
    return wrapper


def make_node(name=None, icon=None, path=None, **kwargs):
    from json import loads
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import get_infolabel, get_localized
    from tmdbhelper.lib.files.futils import get_files_in_folder, read_file
    from tmdbhelper.lib.addon.consts import NODE_BASEDIR
    from tmdbhelper.lib.files.futils import dumps_to_file

    name = name or get_infolabel('Container.ListItem.Label') or ''
    icon = icon or get_infolabel('Container.ListItem.Icon') or ''
    path = path or get_infolabel('Container.ListItem.FolderPath') or ''
    item = {'name': name, 'icon': icon, 'path': path}

    basedir = NODE_BASEDIR
    files = get_files_in_folder(basedir, r'.*\.json')

    x = Dialog().select(get_localized(32504).format(name), [f for f in files] + [get_localized(32495)])
    if x == -1:
        return
    elif x == len(files):
        file = Dialog().input(get_localized(551))
        if not file:
            return
        meta = {
            "name": file,
            "icon": "",
            "list": []}
        file = f'{file}.json'
    else:
        file = files[x]
        data = read_file(basedir + file)
        meta = loads(data) or {}
    if not meta or 'list' not in meta:
        return

    removals = []
    for x, i in enumerate(meta['list']):
        if path != i['path']:
            continue
        if not Dialog().yesno(f'{name}', get_localized(32492).format(name, file)):
            return
        removals.append(x)

    if removals:
        for x in sorted(removals, reverse=True):
            del meta['list'][x]
        text = get_localized(32493).format(name, file)
    else:
        meta['list'].append(item)
        text = get_localized(32494).format(name, file)

    dumps_to_file(meta, basedir, file, join_addon_data=False)
    Dialog().ok(f'{name}', text)


def clean_old_databases():
    """ Once-off routine to delete old unused database versions to avoid wasting disk space """
    from tmdbhelper.lib.files.futils import delete_folder
    from tmdbhelper.lib.addon.plugin import get_setting
    for f in ['database', 'database_v2', 'database_v3', 'database_v4', 'database_v5']:
        delete_folder(f, force=True, check_exists=True)
    save_path = get_setting('image_location', 'str')
    for f in ['blur', 'crop', 'desaturate', 'colors']:
        delete_folder(f, force=True, check_exists=True)
        if not save_path:
            continue
        delete_folder(f'{save_path}{f}/', force=True, check_exists=True, join_addon_data=False)


def mem_cache_kodidb(notification=True):
    from tmdbhelper.lib.addon.plugin import ADDONPATH
    from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
    from tmdbhelper.lib.addon.logger import TimerFunc
    from xbmcgui import Dialog
    with TimerFunc('KodiLibrary sync took', inline=True):
        KodiLibrary('movie', cache_refresh=True)
        KodiLibrary('tvshow', cache_refresh=True)
        if notification:
            Dialog().notification('TMDbHelper', 'Kodi Library cached to memory', icon=f'{ADDONPATH}/icon.png')


def container_refresh():
    from tmdbhelper.lib.addon.tmdate import set_timestamp
    from jurialmunkey.window import get_property
    from tmdbhelper.lib.addon.plugin import executebuiltin
    executebuiltin('Container.Refresh')
    get_property('Widgets.Reload', set_property=f'{set_timestamp(0, True)}')


def split_value(split_value, separator=None, **kwargs):
    """ Split string values and output to window properties """
    from jurialmunkey.window import get_property
    if not split_value:
        return
    v = f'{split_value}'
    s = separator or ' / '
    p = kwargs.get("property") or "TMDbHelper.Split"
    for x, i in enumerate(v.split(s)):
        get_property(f'{p}.{x}', set_property=i, prefix=-1)


def kodi_setting(kodi_setting, **kwargs):
    """ Get Kodi setting value and output to window property """
    from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
    from jurialmunkey.window import get_property
    method = "Settings.GetSettingValue"
    params = {"setting": kodi_setting}
    response = get_jsonrpc(method, params)
    get_property(
        name=kwargs.get('property') or 'KodiSetting',
        set_property=f'{response.get("result", {}).get("value", "")}')


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@get_tmdb_id
def sync_trakt(tmdb_type=None, tmdb_id=None, season=None, episode=None, sync_type=None, **kwargs):
    """ Open sync trakt menu for item """
    from tmdbhelper.lib.script.sync import sync_trakt_item
    from tmdbhelper.lib.addon.plugin import convert_type
    trakt_type = convert_type(tmdb_type, 'trakt', season=season, episode=episode)
    sync_trakt_item(trakt_type=trakt_type, unique_id=tmdb_id, season=season, episode=episode, id_type='tmdb', sync_type=sync_type)


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def manage_artwork(tmdb_id=None, tmdb_type=None, season=None, **kwargs):
    from tmdbhelper.lib.items.builder import ItemBuilder
    ItemBuilder().manage_artwork(tmdb_id=tmdb_id, tmdb_type=tmdb_type, season=season)


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def select_artwork(tmdb_id=None, tmdb_type=None, season=None, **kwargs):
    from tmdbhelper.lib.items.builder import ItemBuilder
    ItemBuilder().select_artwork(tmdb_id=tmdb_id, tmdb_type=tmdb_type, season=season)


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def refresh_details(tmdb_id=None, tmdb_type=None, season=None, episode=None, confirm=True, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.items.builder import ItemBuilder
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.addon.plugin import get_localized
    with BusyDialog():
        details = ItemBuilder().get_item(tmdb_type, tmdb_id, season, episode, cache_refresh=True) or {}
        details = details.get('listitem')
    if details and confirm:
        Dialog().ok('TMDbHelper', get_localized(32234).format(tmdb_type, tmdb_id))
        container_refresh()
    return details


@is_in_kwargs({'tmdb_type': True})
@get_tmdb_id
def related_lists(tmdb_id=None, tmdb_type=None, season=None, episode=None, container_update=True, include_play=False, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.items.basedir import get_basedir_details
    from tmdbhelper.lib.addon.plugin import format_folderpath, encode_url, executebuiltin
    items = get_basedir_details(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode, include_play=include_play)
    if not items or len(items) <= 1:
        return
    choice = Dialog().contextmenu([i.get('label') for i in items])
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
        info=item['params']['info'],
        play='RunPlugin',  # Use RunPlugin to avoid window manager info dialog crash with Browse method
        content='pictures' if item['params']['info'] in ['posters', 'fanart'] else 'videos')
    executebuiltin('Dialog.Close(busydialog)')  # Kill modals because prevents ActivateWindow
    executebuiltin(path)


@is_in_kwargs({'tmdb_type': ['movie', 'tv']})
@choose_tmdb_id
def add_to_library(tmdb_type=None, tmdb_id=None, **kwargs):
    from tmdbhelper.lib.update.library import add_to_library
    add_to_library(info=tmdb_type, tmdb_id=tmdb_id)


@is_in_kwargs({'user_list': True})
def user_list(user_list=None, user_slug=None, **kwargs):
    from tmdbhelper.lib.update.library import add_to_library
    user_slug = user_slug or 'me'
    add_to_library(info='trakt', user_slug=user_slug, list_slug=user_list, confirm=True, allow_update=True, busy_spinner=True)


@is_in_kwargs({'like_list': True})
def like_list(like_list=None, user_slug=None, delete=False, **kwargs):
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    user_slug = user_slug or 'me'
    TraktAPI().like_userlist(user_slug=user_slug, list_slug=like_list, confirmation=True, delete=delete)
    if not delete:
        return
    container_refresh()


@is_in_kwargs({'delete_list': True})
def delete_list(delete_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    if not Dialog().yesno(get_localized(32358), get_localized(32357).format(delete_list)):
        return
    TraktAPI().delete_response('users/me/lists', delete_list)
    container_refresh()


@is_in_kwargs({'rename_list': True})
def rename_list(rename_list=None, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.addon.plugin import get_localized
    name = Dialog().input(get_localized(32359))
    if not name:
        return
    TraktAPI().post_response('users/me/lists', rename_list, postdata={'name': name}, response_method='put')
    container_refresh()


def blur_image(blur_image=None, **kwargs):
    from tmdbhelper.lib.monitor.images import ImageFunctions
    blur_img = ImageFunctions(method='blur', artwork=blur_image)
    blur_img.setName('blur_img')
    blur_img.start()


def image_colors(image_colors=None, **kwargs):
    from tmdbhelper.lib.monitor.images import ImageFunctions
    image_colors = ImageFunctions(method='colors', artwork=image_colors)
    image_colors.setName('image_colors')
    image_colors.start()


def provider_allowlist():
    from xbmcgui import Dialog
    from tmdbhelper.lib.api.tmdb.api import TMDb
    from tmdbhelper.lib.addon.plugin import get_localized, get_setting, set_setting
    tmdb_api = TMDb()

    def _get_available_providers():
        available_providers = set()
        for tmdb_type in ['movie', 'tv']:
            results = tmdb_api.get_request_lc('watch/providers', tmdb_type, watch_region=tmdb_api.iso_country).get('results')
            if not results:
                continue
            available_providers |= {i.get('provider_name') for i in results}
        return available_providers

    available_providers = _get_available_providers()
    if not available_providers:
        return
    available_providers = sorted(available_providers)

    provider_allowlist = get_setting('provider_allowlist', 'str')
    provider_allowlist = provider_allowlist.split(' | ') if provider_allowlist else []
    preselected = [x for x, i in enumerate(available_providers) if not provider_allowlist or i in provider_allowlist]
    indices = Dialog().multiselect(get_localized(32437), available_providers, preselect=preselected)
    if indices is None:
        return

    selected_providers = [available_providers[x] for x in indices]
    if not selected_providers:
        return
    set_setting('provider_allowlist', ' | '.join(selected_providers), 'str')
    Dialog().ok(get_localized(32438), get_localized(32439))


def update_players():
    from xbmcgui import Dialog
    from tmdbhelper.lib.files.downloader import Downloader
    from tmdbhelper.lib.addon.plugin import set_setting
    from tmdbhelper.lib.addon.plugin import get_setting
    from tmdbhelper.lib.addon.plugin import get_localized
    players_url = get_setting('players_url', 'str')
    players_url = Dialog().input(get_localized(32313), defaultt=players_url)
    if not Dialog().yesno(
            get_localized(32032),
            get_localized(32314).format(players_url)):
        return
    set_setting('players_url', players_url, 'str')
    downloader = Downloader(
        extract_to='special://profile/addon_data/plugin.video.themoviedb.helper/players',
        download_url=players_url)
    downloader.get_extracted_zip()


def set_defaultplayer(**kwargs):
    from tmdbhelper.lib.player.players import Players
    from tmdbhelper.lib.addon.plugin import set_setting
    tmdb_type = kwargs.get('set_defaultplayer')
    setting_name = 'default_player_movies' if tmdb_type == 'movie' else 'default_player_episodes'
    default_player = Players(tmdb_type).select_player(detailed=True, clear_player=True)
    if not default_player:
        return
    if not default_player.get('file') or not default_player.get('mode'):
        return set_setting(setting_name, '', 'str')
    set_setting(setting_name, f'{default_player["file"]} {default_player["mode"]}', 'str')


def set_chosenplayer(tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
    """
    Prompts user to select (or clear) a default player for a single movie or tvshow
    """
    from xbmcgui import Dialog
    from tmdbhelper.lib.player.players import Players
    from tmdbhelper.lib.addon.consts import PLAYERS_CHOSEN_DEFAULTS_FILENAME
    from tmdbhelper.lib.files.futils import get_json_filecache, set_json_filecache
    from tmdbhelper.lib.addon.plugin import get_localized

    if tmdb_type not in ['movie', 'tv'] or not tmdb_id:
        return

    obj = get_json_filecache(PLAYERS_CHOSEN_DEFAULTS_FILENAME) or {}
    lvl = obj
    itm = obj.setdefault(tmdb_type, {}).setdefault(tmdb_id, {})
    nme = kwargs.get('set_chosenplayer') or ''
    itm['name'] = nme

    # If theres a season/episode value then ask user if want to set for whole tvshow or just season/episode
    x = 0
    if season is not None:
        func = Dialog()
        opts = {'nolabel': get_localized(20364), 'yeslabel': get_localized(20373)}

        if episode is not None:
            func = func.yesnocustom
            opts['customlabel'] = get_localized(20359)
        else:
            func = func.yesno

        x = func(f'{tmdb_type} - {tmdb_id}', get_localized(32477), **opts)

        if x == -1:
            return
        if x in [1, 2]:
            lvl = itm.setdefault('season', {})
            itm = lvl.setdefault(f'{season}', {})
        if x == 2:
            lvl = itm.setdefault('episode', {})
            itm = lvl.setdefault(f'{episode}', {})

    chosen_player = Players(tmdb_type).select_player(detailed=True, clear_player=True)
    if not chosen_player:
        return

    if chosen_player.get('file') and chosen_player.get('mode'):
        itm['file'] = chosen_player["file"]
        itm['mode'] = chosen_player["mode"]
        msg = get_localized(32474).format(f"{itm['file']} {itm['mode']}", nme)

    else:
        obj[tmdb_type].pop(f'{tmdb_id}')
        msg = get_localized(32475).format(nme)

    set_json_filecache(obj, PLAYERS_CHOSEN_DEFAULTS_FILENAME, 0)
    Dialog().ok(f'{tmdb_type} - {tmdb_id}', msg)


def library_autoupdate(**kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.update.userlist import library_autoupdate as _library_autoupdate
    from tmdbhelper.lib.addon.plugin import get_localized
    if kwargs.get('force') == 'select':
        choice = Dialog().yesno(
            get_localized(32391),
            get_localized(32392),
            yeslabel=get_localized(32393),
            nolabel=get_localized(32394))
        if choice == -1:
            return
        kwargs['force'] = True if choice else False
    _library_autoupdate(
        list_slugs=kwargs.get('list_slug', None),
        user_slugs=kwargs.get('user_slug', None),
        busy_spinner=True if kwargs.get('busy_dialog', False) else False,
        force=kwargs.get('force', False))


def log_request(**kwargs):
    import xbmcvfs
    from json import dumps
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.api.tmdb.api import TMDb
    from tmdbhelper.lib.api.tvdb.api import TVDb
    from tmdbhelper.lib.files.futils import validify_filename
    from tmdbhelper.lib.files.futils import dumps_to_file
    with BusyDialog():
        kwargs['response'] = None
        if not kwargs.get('url'):
            kwargs['url'] = Dialog().input('URL')
        if not kwargs['url']:
            return
        if kwargs.get('log_request').lower() == 'trakt':
            kwargs['response'] = TraktAPI().get_response_json(kwargs['url'])
        elif kwargs.get('log_request').lower() == 'tvdb':
            kwargs['response'] = TVDb().get_response_json(kwargs['url'])
        else:
            kwargs['response'] = TMDb().get_response_json(kwargs['url'])
        if not kwargs['response']:
            Dialog().ok(kwargs['log_request'].capitalize(), f'{kwargs["url"]}\nNo Response!')
            return
        filename = validify_filename(f'{kwargs["log_request"]}_{kwargs["url"]}.json')
        dumps_to_file(kwargs, 'log_request', filename)
        msg = (
            f'[B]{kwargs["url"]}[/B]\n\n{xbmcvfs.translatePath("special://profile/addon_data/")}\n'
            f'plugin.video.themoviedb.helper/log_request\n{filename}')
        Dialog().ok(kwargs['log_request'].capitalize(), msg)
        Dialog().textviewer(filename, dumps(kwargs['response'], indent=2))


def log_sync(log_sync, trakt_type='show', id_type=None, extended=None, **kwargs):
    from json import dumps
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.dialog import BusyDialog
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.files.futils import validify_filename
    from tmdbhelper.lib.files.futils import dumps_to_file
    with BusyDialog():
        data = TraktAPI().get_sync(log_sync, trakt_type, id_type=id_type, extended=extended)
        filename = validify_filename(f'sync__{log_sync}_{trakt_type}_{id_type}_{extended}.json')
        dumps_to_file(data, 'log_request', filename)
        Dialog().textviewer(filename, dumps(data, indent=2))


def delete_cache(delete_cache, **kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.items.builder import ItemBuilder
    from tmdbhelper.lib.api.fanarttv.api import FanartTV
    from tmdbhelper.lib.api.trakt.api import TraktAPI
    from tmdbhelper.lib.api.tmdb.api import TMDb
    from tmdbhelper.lib.api.omdb.api import OMDb
    from tmdbhelper.lib.addon.plugin import get_localized
    from tmdbhelper.lib.addon.dialog import BusyDialog
    d = {
        'TMDb': lambda: TMDb(),
        'Trakt': lambda: TraktAPI(),
        'FanartTV': lambda: FanartTV(),
        'OMDb': lambda: OMDb(),
        'Item Details': lambda: ItemBuilder()}
    if delete_cache == 'select':
        m = [i for i in d]
        x = Dialog().contextmenu([get_localized(32387).format(i) for i in m])
        if x == -1:
            return
        delete_cache = m[x]
    z = d.get(delete_cache)
    if not z:
        return
    if not Dialog().yesno(get_localized(32387).format(delete_cache), get_localized(32388).format(delete_cache)):
        return
    with BusyDialog():
        z()._cache.ret_cache()._do_delete()
    Dialog().ok(get_localized(32387).format(delete_cache), get_localized(32389))


@map_kwargs({'play': 'tmdb_type'})
@get_tmdb_id
def play_external(**kwargs):
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.player.players import Players
    kodi_log(['lib.script.router - attempting to play\n', kwargs], 1)
    Players(**kwargs).play()


def play_using(play_using, mode='play', **kwargs):
    from tmdbhelper.lib.addon.plugin import get_infolabel
    from tmdbhelper.lib.files.futils import read_file
    from jurialmunkey.parser import parse_paramstring

    def _update_from_listitem(dictionary):
        url = get_infolabel('ListItem.FileNameAndPath') or ''
        if url[-5:] == '.strm':
            url = read_file(url)
        params = {}
        if url.startswith('plugin://plugin.video.themoviedb.helper/?'):
            params = parse_paramstring(url.replace('plugin://plugin.video.themoviedb.helper/?', ''))
        if params.pop('info', None) in ['play', 'related']:
            dictionary.update(params)
        if dictionary.get('tmdb_type'):
            return dictionary
        dbtype = get_infolabel('ListItem.DBType')
        if dbtype == 'movie':
            dictionary['tmdb_type'] = 'movie'
            dictionary['tmdb_id'] = get_infolabel('ListItem.UniqueId(tmdb)')
            dictionary['imdb_id'] = get_infolabel('ListItem.UniqueId(imdb)')
            dictionary['query'] = get_infolabel('ListItem.Title')
            dictionary['year'] = get_infolabel('ListItem.Year')
            if dictionary['tmdb_id'] or dictionary['imdb_id'] or dictionary['query']:
                return dictionary
        elif dbtype == 'episode':
            dictionary['tmdb_type'] = 'tv'
            dictionary['query'] = get_infolabel('ListItem.TVShowTitle')
            dictionary['ep_year'] = get_infolabel('ListItem.Year')
            dictionary['season'] = get_infolabel('ListItem.Season')
            dictionary['episode'] = get_infolabel('ListItem.Episode')
            if dictionary['query'] and dictionary['season'] and dictionary['episode']:
                return dictionary

    if 'tmdb_type' not in kwargs and not _update_from_listitem(kwargs):
        return
    kwargs['mode'] = mode
    kwargs['player'] = play_using
    play_external(**kwargs)


def sort_list(**kwargs):
    from xbmcgui import Dialog
    from tmdbhelper.lib.addon.plugin import executebuiltin, format_folderpath, encode_url
    from tmdbhelper.lib.api.trakt.api import get_sort_methods
    sort_methods = get_sort_methods(kwargs['info'])
    x = Dialog().contextmenu([i['name'] for i in sort_methods])
    if x == -1:
        return
    for k, v in sort_methods[x]['params'].items():
        kwargs[k] = v
    executebuiltin(format_folderpath(encode_url(**kwargs)))


def do_wikipedia_gui(wikipedia, tmdb_type=None, **kwargs):
    from xbmc import executebuiltin
    from tmdbhelper.lib.addon.plugin import get_language
    language = get_language()[:2]
    cmd = f'script.wikipedia,wikipedia={wikipedia},xml_file=script-tmdbhelper-wikipedia.xml'
    if tmdb_type:
        cmd = f'{cmd},tmdb_type={tmdb_type}'
    if language:
        cmd = f'{cmd},language={language}'
    executebuiltin(f'RunScript({cmd})')
