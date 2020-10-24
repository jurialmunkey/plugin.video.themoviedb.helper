import re
import sys
import xbmc
import xbmcgui
import xbmcaddon
import datetime
from resources.lib.helpers.rpc import get_jsonrpc, get_directory, KodiLibrary
from resources.lib.helpers.constants import PLAYERS_URLENCODE, PLAYERS_BASEDIR_BUNDLED, PLAYERS_BASEDIR_USER
from resources.lib.helpers.window import get_property
from resources.lib.tmdb.api import TMDb
from resources.lib.trakt.api import TraktAPI
from resources.lib.items.listitem import ListItem
from resources.lib.helpers.plugin import ADDON, PLUGINPATH, ADDONPATH, viewitems, kodi_log
from resources.lib.helpers.parser import try_int, try_decode, try_encode
from resources.lib.helpers.setutils import del_empty_keys
from resources.lib.helpers.fileutils import get_files_in_folder, read_file, normalise_filesize
from resources.lib.helpers.decorators import busy_dialog
from json import loads, dumps
from string import Formatter
from collections import defaultdict
from threading import Thread
try:
    from urllib.parse import quote_plus, quote  # Py3
except ImportError:
    from urllib import quote_plus, quote  # Py2
if sys.version_info[0] >= 3:
    unicode = str  # In Py3 str is now unicode


def string_format_map(fmt, d):
    try:
        str.format_map
    except AttributeError:
        parts = Formatter().parse(fmt)
        return fmt.format(**{part[1]: d[part[1]] for part in parts})
    else:
        return fmt.format(**d)


def add_to_queue(episodes, clear_playlist=False, play_next=False):
    if not episodes:
        return
    playlist = xbmc.PlayList(1)
    if clear_playlist:
        playlist.clear()
    for i in episodes:
        li = ListItem(**i)
        li.set_params_reroute()
        playlist.add(li.get_url(), li.get_listitem())
    if play_next:
        xbmc.Player().play(playlist)


class KeyboardInputter(Thread):
    def __init__(self, action=None, text=None, timeout=300):
        Thread.__init__(self)
        self.text = text
        self.action = action
        self.exit = False
        self.poll = 0.5
        self.timeout = timeout

    def run(self):
        while not xbmc.Monitor().abortRequested() and not self.exit and self.timeout > 0:
            xbmc.Monitor().waitForAbort(self.poll)
            self.timeout -= self.poll
            if self.text and xbmc.getCondVisibility("Window.IsVisible(DialogKeyboard.xml)"):
                get_jsonrpc("Input.SendText", {"text": self.text, "done": True})
                self.exit = True
            elif self.action and xbmc.getCondVisibility("Window.IsVisible(DialogSelect.xml) | Window.IsVisible(DialogConfirm.xml)"):
                get_jsonrpc(self.action)
                self.exit = True


class Players(object):
    def __init__(self, tmdb_type, tmdb_id=None, season=None, episode=None, **kwargs):
        with busy_dialog():
            self.players = self._get_players_from_file()
            self.details = self._get_item_details(tmdb_type, tmdb_id, season, episode)
            self.item = self._get_detailed_item(tmdb_type, tmdb_id, season, episode) or {}
            self.dialog_players = self._get_players_for_dialog(tmdb_type)
            self.playerstring = self._get_playerstring(tmdb_type, tmdb_id, season, episode)
            self.default_player = ADDON.getSettingString('default_player_movies') if tmdb_type == 'movie' else ADDON.getSettingString('default_player_episodes')

    def _get_playerstring(self, tmdb_type, tmdb_id, season=None, episode=None):
        if not self.details:
            return None
        playerstring = {}
        playerstring['tmdb_type'] = 'episode' if tmdb_type in ['episode', 'tv'] else 'movie'
        playerstring['tmdb_id'] = tmdb_id
        playerstring['imdb_id'] = self.details.unique_ids.get('imdb')
        if tmdb_type in ['episode', 'tv']:
            playerstring['imdb_id'] = self.details.unique_ids.get('tvshow.imdb')
            playerstring['tvdb_id'] = self.details.unique_ids.get('tvshow.tvdb')
            playerstring['season'] = season
            playerstring['episode'] = episode
        return dumps(del_empty_keys(playerstring))

    def _check_assert(self, keys=[]):
        if not self.item:
            return True  # No item so no need to assert values as we're only building to choose default player
        for i in keys:
            if i.startswith('!'):  # Inverted assert check for NOT value
                if self.item.get(i[1:]) and self.item.get(i[1:]) != 'None':
                    return False  # Key has a value so player fails assert check
            else:  # Standard assert check for value
                if not self.item.get(i) or self.item.get(i) == 'None':
                    return False  # Key didn't have a value so player fails assert check
        return True  # Player passed the assert check

    def _get_built_player(self, file, mode, value=None):
        value = value or self.players.get(file) or {}
        if mode in ['play_movie', 'play_episode']:
            name = ADDON.getLocalizedString(32061)
            is_folder = False
        else:
            name = xbmc.getLocalizedString(137)
            is_folder = True
        return {
            'file': file, 'mode': mode,
            'is_folder': is_folder,
            'name': '{} {}'.format(name, value.get('name')),
            'plugin_name': value.get('plugin'),
            'plugin_icon': value.get('icon', '').format(ADDONPATH) or xbmcaddon.Addon(value.get('plugin', '')).getAddonInfo('icon'),
            'fallback': value.get('fallback', {}).get(mode),
            'actions': value.get(mode)}

    def _get_local_item(self, tmdb_type):
        file = self._get_local_movie() if tmdb_type == 'movie' else self._get_local_episode()
        if not file:
            return []
        return [{
            'name': '{} Kodi'.format(ADDON.getLocalizedString(32061)),
            'is_folder': False,
            'is_local': True,
            'plugin_name': 'xbmc.core',
            'plugin_icon': '{}/resources/icons/other/kodi.png'.format(ADDONPATH),
            'actions': file}]

    def _get_local_file(self, file):
        if not file:
            return
        if file.endswith('.strm'):
            contents = read_file(file)
            if contents.startswith('plugin://plugin.video.themoviedb.helper'):
                return
        return file

    def _get_local_movie(self):
        return self._get_local_file(KodiLibrary(dbtype='movie').get_info(
            'file', fuzzy_match=False,
            tmdb_id=self.item.get('tmdb'),
            imdb_id=self.item.get('imdb')))

    def _get_local_episode(self):
        dbid = KodiLibrary(dbtype='tvshow').get_info(
            'dbid', fuzzy_match=False,
            tmdb_id=self.item.get('tmdb'),
            tvdb_id=self.item.get('tvdb'),
            imdb_id=self.item.get('imdb'))
        return self._get_local_file(KodiLibrary(dbtype='episode', tvshowid=dbid).get_info(
            'file', season=self.item.get('season'), episode=self.item.get('episode')))

    def _get_players_for_dialog(self, tmdb_type):
        if tmdb_type not in ['movie', 'tv']:
            return []
        dialog_play = self._get_local_item(tmdb_type)
        dialog_search = []
        for k, v in sorted(viewitems(self.players), key=lambda i: try_int(i[1].get('priority')) or 1000):
            if tmdb_type == 'movie':
                if v.get('play_movie') and self._check_assert(v.get('assert', {}).get('play_movie', [])):
                    dialog_play.append(self._get_built_player(file=k, mode='play_movie', value=v))
                if v.get('search_movie') and self._check_assert(v.get('assert', {}).get('search_movie', [])):
                    dialog_search.append(self._get_built_player(file=k, mode='search_movie', value=v))
            else:
                if v.get('play_episode') and self._check_assert(v.get('assert', {}).get('play_episode', [])):
                    dialog_play.append(self._get_built_player(file=k, mode='play_episode', value=v))
                if v.get('search_episode') and self._check_assert(v.get('assert', {}).get('search_episode', [])):
                    dialog_search.append(self._get_built_player(file=k, mode='search_episode', value=v))
        return dialog_play + dialog_search

    def _get_players_from_file(self):
        players = {}
        basedirs = [PLAYERS_BASEDIR_USER]
        if ADDON.getSettingBool('bundled_players'):
            basedirs += [PLAYERS_BASEDIR_BUNDLED]
        for basedir in basedirs:
            files = get_files_in_folder(basedir, r'.*\.json')
            for file in files:
                meta = loads(read_file(basedir + file)) or {}
                plugins = meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
                plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
                for i in plugins:
                    if not xbmc.getCondVisibility(u'System.HasAddon({0})'.format(i)):
                        break  # System doesn't have a required plugin so skip this player
                else:
                    players[file] = meta
        return players

    def get_external_ids(self, li, season=None, episode=None):
        trakt_api = TraktAPI()
        unique_id, trakt_type = None, None
        if li.infolabels.get('mediatype') == 'movie':
            unique_id = li.unique_ids.get('tmdb')
            trakt_type = 'movie'
        elif li.infolabels.get('mediatype') == 'tvshow':
            unique_id = li.unique_ids.get('tmdb')
            trakt_type = 'show'
        elif li.infolabels.get('mediatype') in ['season', 'episode']:
            unique_id = li.unique_ids.get('tvshow.tmdb')
            trakt_type = 'show'
        if not unique_id or not trakt_type:
            return
        trakt_slug = trakt_api.get_id(id_type='tmdb', unique_id=unique_id, trakt_type=trakt_type, output_type='slug')
        if not trakt_slug:
            return
        details = trakt_api.get_details(trakt_type, trakt_slug, extended=None)
        if not details:
            return
        if li.infolabels.get('mediatype') in ['movie', 'tvshow', 'season']:
            return {
                'unique_ids': {
                    'tmdb': unique_id,
                    'tvdb': details.get('ids', {}).get('tvdb'),
                    'imdb': details.get('ids', {}).get('imdb'),
                    'slug': details.get('ids', {}).get('slug'),
                    'trakt': details.get('ids', {}).get('trakt')}}
        episode_details = trakt_api.get_details(
            trakt_type, trakt_slug,
            season=season or li.infolabels.get('season'),
            episode=episode or li.infolabels.get('episode'),
            extended=None)
        if episode_details:
            return {
                'unique_ids': {
                    'tvshow.tmdb': unique_id,
                    'tvshow.tvdb': details.get('ids', {}).get('tvdb'),
                    'tvshow.imdb': details.get('ids', {}).get('imdb'),
                    'tvshow.slug': details.get('ids', {}).get('slug'),
                    'tvshow.trakt': details.get('ids', {}).get('trakt'),
                    'tvdb': episode_details.get('ids', {}).get('tvdb'),
                    'tmdb': episode_details.get('ids', {}).get('tmdb'),
                    'imdb': episode_details.get('ids', {}).get('imdb'),
                    'slug': episode_details.get('ids', {}).get('slug'),
                    'trakt': episode_details.get('ids', {}).get('trakt')}}

    def _get_item_details(self, tmdb_type, tmdb_id, season=None, episode=None):
        details = TMDb().get_details(tmdb_type, tmdb_id, season, episode)
        if not details:
            return None
        details = ListItem(**details)
        details.infolabels['mediatype'] == 'movie' if tmdb_type == 'movie' else 'episode'
        details.set_details(details=self.get_external_ids(details, season=season, episode=episode))
        return details

    def _get_detailed_item(self, tmdb_type, tmdb_id, season=None, episode=None):
        details = self.details or self._get_item_details(tmdb_type, tmdb_id, season, episode)
        if not details:
            return None
        item = defaultdict(lambda: '+')
        item['id'] = item['tmdb'] = tmdb_id
        item['imdb'] = details.unique_ids.get('imdb')
        item['tvdb'] = details.unique_ids.get('tvdb')
        item['trakt'] = details.unique_ids.get('trakt')
        item['slug'] = details.unique_ids.get('slug')
        item['season'] = season
        item['episode'] = episode
        item['originaltitle'] = details.infolabels.get('originaltitle')
        item['title'] = details.infolabels.get('tvshowtitle') or details.infolabels.get('title')
        item['showname'] = item['clearname'] = item['tvshowtitle'] = item.get('title')
        item['year'] = details.infolabels.get('year')
        item['name'] = u'{} ({})'.format(item.get('title'), item.get('year'))
        item['premiered'] = item['firstaired'] = item['released'] = details.infolabels.get('premiered')
        item['plot'] = details.infolabels.get('plot')
        item['cast'] = item['actors'] = " / ".join([i.get('name') for i in details.cast if i.get('name')])
        item['thumbnail'] = details.art.get('thumb')
        item['poster'] = details.art.get('poster')
        item['fanart'] = details.art.get('fanart')
        item['now'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        if tmdb_type == 'tv' and season is not None and episode is not None:
            item['id'] = item['epid'] = item['eptvdb'] = item.get('tvdb')
            item['title'] = details.infolabels.get('title')  # Set Episode Title
            item['name'] = u'{0} S{1:02d}E{2:02d}'.format(item.get('showname'), try_int(season), try_int(episode))
            item['season'] = season
            item['episode'] = episode
            item['showpremiered'] = details.infoproperties.get('tvshow.premiered')
            item['showyear'] = details.infoproperties.get('tvshow.year')
            item['eptmdb'] = details.unique_ids.get('tmdb')
            item['epimdb'] = details.unique_ids.get('imdb')
            item['eptrakt'] = details.unique_ids.get('trakt')
            item['epslug'] = details.unique_ids.get('slug')
            item['tmdb'] = details.unique_ids.get('tvshow.tmdb')
            item['imdb'] = details.unique_ids.get('tvshow.imdb')
            item['trakt'] = details.unique_ids.get('tvshow.trakt')
            item['slug'] = details.unique_ids.get('tvshow.slug')

        for k, v in viewitems(item.copy()):
            if k not in PLAYERS_URLENCODE:
                continue
            v = u'{0}'.format(v)
            for key, value in viewitems({k: v, '{}_meta'.format(k): dumps(v)}):
                item[key] = value.replace(',', '')
                item[key + '_+'] = value.replace(',', '').replace(' ', '+')
                item[key + '_-'] = value.replace(',', '').replace(' ', '-')
                item[key + '_escaped'] = quote(quote(try_encode(value)))
                item[key + '_escaped+'] = quote(quote_plus(try_encode(value)))
                item[key + '_url'] = quote(try_encode(value))
                item[key + '_url+'] = quote_plus(try_encode(value))
        return item

    def select_player(self, detailed=True, clear_player=False):
        """ Returns user selected player via dialog - detailed bool switches dialog style """
        dialog_players = [] if not clear_player else [{
            'name': ADDON.getLocalizedString(32311),
            'plugin_name': 'plugin.video.themoviedb.helper',
            'plugin_icon': '{}/resources/icons/other/kodi.png'.format(ADDONPATH)}]
        dialog_players += self.dialog_players
        players = [ListItem(
            label=i.get('name'),
            label2='{} v{}'.format(i.get('plugin_name'), xbmcaddon.Addon(i.get('plugin_name', '')).getAddonInfo('version')),
            art={'thumb': i.get('plugin_icon')}).get_listitem() for i in dialog_players]
        x = xbmcgui.Dialog().select(ADDON.getLocalizedString(32042), players, useDetails=detailed)
        if x == -1:
            return {}
        player = dialog_players[x]
        player['idx'] = x
        return player

    def _get_player_fallback(self, fallback):
        if not fallback:
            return
        file, mode = fallback.split()
        if not file or not mode:
            return
        player = self._get_built_player(file, mode)
        if not player:
            return
        for x, i in enumerate(self.dialog_players):
            if i == player:
                player['idx'] = x
                return player

    def _get_path_from_rules(self, folder, action):
        """ Returns tuple of (path, is_folder) """
        for x, f in enumerate(folder):
            for k, v in viewitems(action):  # Iterate through our key (infolabel) / value (infolabel must match) pairs of our action
                if k == 'position':  # We're looking for an item position not an infolabel
                    if try_int(string_format_map(v, self.item)) != x + 1:  # Format our position value and add one since people are dumb and don't know that arrays start at 0
                        break  # Not the item position we want so let's go to next item in folder
                elif not f.get(k) or not re.match(string_format_map(v, self.item), u'{}'.format(f.get(k, ''))):  # Format our value and check if it regex matches the infolabel key
                    break  # Item's key value doesn't match value we are looking for so let's got to next item in folder
            else:  # Item matched our criteria so let's return it
                if f.get('file'):
                    is_folder = False if f.get('filetype') == 'file' else True  # Set false for files so we can play
                    return (f.get('file'), is_folder)   # Get ListItem.FolderPath for item and return as player

    def _player_dialog_select(self, folder, auto=False):
        d_items = []
        for f in folder:

            # Skip items without labels as probably not worth playing
            if not f.get('label') or f.get('label') == 'None':
                continue

            # Get the label of the item
            label_a = f.get('label')

            # Add year to our label if exists and not special value of 1601
            if f.get('year') and f.get('year') != 1601:
                label_a = u'{} ({})'.format(label_a, f.get('year'))

            # Add season and episode numbers to label
            if try_int(f.get('season', 0)) > 0 and try_int(f.get('episode', 0)) > 0:
                label_a = u'{}x{}. {}'.format(f.get('season'), f.get('episode'), label_a)

            # Add various stream details to ListItem.Label2 (aka label_b)
            label_b_list = []
            if f.get('streamdetails'):
                sdv_list = f.get('streamdetails', {}).get('video', [{}]) or [{}]
                sda_list = f.get('streamdetails', {}).get('audio', [{}]) or [{}]
                sdv, sda = sdv_list[0], sda_list[0]
                if sdv.get('width') or sdv.get('height'):
                    label_b_list.append(u'{}x{}'.format(sdv.get('width'), sdv.get('height')))
                if sdv.get('codec'):
                    label_b_list.append(u'{}'.format(sdv.get('codec', '').upper()))
                if sda.get('codec'):
                    label_b_list.append(u'{}'.format(sda.get('codec', '').upper()))
                if sda.get('channels'):
                    label_b_list.append(u'{} CH'.format(sda.get('channels', '')))
                for i in sda_list:
                    if i.get('language'):
                        label_b_list.append(u'{}'.format(i.get('language', '').upper()))
                if sdv.get('duration'):
                    label_b_list.append(u'{} mins'.format(try_int(sdv.get('duration', 0)) // 60))
            if f.get('size'):
                label_b_list.append(u'{}'.format(normalise_filesize(f.get('size', 0))))
            label_b = ' | '.join(label_b_list) if label_b_list else ''

            # Add item to select dialog list
            d_items.append(ListItem(label=label_a, label2=label_b, art={'thumb': f.get('thumbnail')}).get_listitem())

        if not d_items:
            return -1  # No items so ask user to select new player

        # If autoselect enabled and only 1 item choose that otherwise ask user to choose
        idx = 0 if auto and len(d_items) == 1 else xbmcgui.Dialog().select(ADDON.getLocalizedString(32236), d_items, useDetails=True)

        if idx == -1:
            return  # User exited the dialog so return nothing

        is_folder = False if folder[idx].get('filetype') == 'file' else True
        return (folder[idx].get('file'), is_folder)  # Return the player

    def _get_path_from_actions(self, actions, is_folder=True):
        """ Returns tuple of (path, is_folder) """
        keyboard_input = None
        path = (actions[0], is_folder)
        for action in actions[1:]:
            # Check if we've got a playable item already
            if not is_folder:
                return path

            # Start thread with keyboard inputter if needed
            if action.get('keyboard'):
                if action.get('keyboard') in ['Up', 'Down', 'Left', 'Right', 'Select']:
                    keyboard_input = KeyboardInputter(action="Input.{}".format(action.get('keyboard')))
                else:
                    keyboard_input = KeyboardInputter(text=string_format_map(action.get('keyboard', ''), self.item))
                keyboard_input.setName('keyboard_input')
                keyboard_input.start()
                continue  # Go to next action

            # Get the next folder from the plugin
            with busy_dialog():
                folder = get_directory(string_format_map(path[0], self.item))

            # Kill our keyboard inputter thread
            if keyboard_input:
                keyboard_input.exit = True
                keyboard_input = None

            # Special option to show dialog of items to select
            if action.get('dialog'):
                auto = True if action.get('dialog', '').lower() == 'auto' else False
                return self._player_dialog_select(folder, auto=auto)

            # Apply the rules for the current action and grab the path
            path = self._get_path_from_rules(folder, action)
            if not path:
                return
        return path

    def _get_path_from_player(self, player=None):
        """ Returns tuple of (path, is_folder) """
        if not player or not isinstance(player, dict):
            return
        actions = player.get('actions')
        if not actions:
            return
        if isinstance(actions, list):
            return self._get_path_from_actions(actions)
        if isinstance(actions, unicode) or isinstance(actions, str):
            return (string_format_map(actions, self.item), player.get('is_folder', False))  # Single path so return it formatted

    def get_default_player(self):
        """ Returns default player """
        # Check local first if we have the setting
        if ADDON.getSettingBool('default_player_local') and self.dialog_players[0].get('is_local'):
            player = self.dialog_players[0]
            player['idx'] = 0
            return player
        if not self.default_player:
            return
        all_players = [u'{} {}'.format(i.get('file'), i.get('mode')) for i in self.dialog_players]
        try:
            x = all_players.index(self.default_player)
        except Exception:
            return
        player = self.dialog_players[x]
        player['idx'] = x
        return player

    def _get_resolved_path(self, player=None, allow_default=False):
        if not player and allow_default:
            player = self.get_default_player()
        player = player or self.select_player()
        if not player:
            return
        path = self._get_path_from_player(player)
        if not path:
            if player.get('idx') is not None:
                del self.dialog_players[player['idx']]  # Remove out player so we don't re-ask user for it
            fallback = self._get_player_fallback(player['fallback']) if player.get('fallback') else None
            return self._get_resolved_path(fallback)
        return path

    def get_resolved_path(self, return_listitem=True):
        if not self.item:
            return
        get_property('PlayerInfoString', clear_property=True)
        path = self._get_resolved_path(allow_default=True)
        if return_listitem:
            self.details.path = path[0] if path else None
            self.details.params = {}
            self.details.infoproperties['is_folder'] = 'false' if path and not path[1] else 'true'
            path = self.details.get_listitem()
        return path

    def _update_listing_hack(self, folder_path=None, reset_focus=None):
        """
        Some plugins use container.update after search results to rewrite path history
        This is a quick hack to rewrite the path back to our original path before updating
        """
        if not folder_path or xbmc.getInfoLabel("Container.FolderPath") == folder_path:
            return
        xbmc.executebuiltin('Container.Update({},replace)'.format(folder_path))
        if not reset_focus:
            return
        with busy_dialog():
            timeout = 20
            while not xbmc.Monitor().abortRequested() and xbmc.getInfoLabel("Container.FolderPath") != folder_path and timeout > 0:
                xbmc.Monitor().waitForAbort(0.25)
                timeout -= 1
            xbmc.executebuiltin(reset_focus)
            xbmc.Monitor().waitForAbort(0.5)

    def play(self, folder_path=None, reset_focus=None):
        # Get some info about current container for container update hack
        if not folder_path:
            folder_path = xbmc.getInfoLabel("Container.FolderPath")
        if not reset_focus and folder_path:
            containerid = xbmc.getInfoLabel("System.CurrentControlID")
            current_pos = xbmc.getInfoLabel("Container({}).CurrentItem".format(containerid))
            reset_focus = 'SetFocus({},{},absolute)'.format(containerid, try_int(current_pos) - 1)

        # Get the resoved path
        listitem = self.get_resolved_path()
        path = listitem.getPath()
        is_folder = True if listitem.getProperty('is_folder') == 'true' else False

        # Wait a moment because sometimes Kodi crashes if we call the plugin to play too quickly!!!
        with busy_dialog():
            xbmc.Monitor().waitForAbort(1)

        # Reset folder hack
        self._update_listing_hack(folder_path=folder_path, reset_focus=reset_focus)

        # Check we have an actual path to open
        if not path or path == PLUGINPATH:
            return

        # Strm files need to play with PlayMedia() to resolve properly
        # Send to xbmc.Player() over PlayMedia() for urls so we can merge our listitem details
        # Using setResolvedUrl directly isn't possible because external addon might need to resolve itself first
        # Also some addons don't resolve using isPlayable and run a command instead or need to open folder
        action = None
        if not is_folder and path.endswith('.strm'):
            action = u'PlayMedia(\"{0}\")'.format(path)
        elif is_folder and xbmc.getCondVisibility("Window.IsMedia"):
            action = u'Container.Update({0})'.format(path)
        elif is_folder:
            action = u'ActivateWindow(videos,{0},return)'.format(path)
        # elif not is_folder:  # Uncomment to send url to PlayMedia rather than xbmc.Player()
        #     action = u'PlayMedia(\"{0}\")'.format(path)

        if not is_folder and self.playerstring:
            get_property('PlayerInfoString', set_property=self.playerstring)

        if action:
            xbmc.executebuiltin(try_encode(try_decode(action)))
        elif not is_folder:
            xbmc.Player().play(path, listitem)
