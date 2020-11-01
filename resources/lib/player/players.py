import re
import sys
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from resources.lib.kodi.rpc import get_directory, KodiLibrary
from resources.lib.addon.window import get_property
from resources.lib.container.listitem import ListItem
from resources.lib.addon.plugin import ADDON, PLUGINPATH, ADDONPATH, viewitems, format_folderpath, kodi_log
from resources.lib.addon.parser import try_int, try_decode, try_encode
from resources.lib.files.utils import read_file, normalise_filesize
from resources.lib.addon.decorators import busy_dialog
from resources.lib.player.details import get_item_details, get_detailed_item, get_playerstring
from resources.lib.player.inputter import KeyboardInputter
from resources.lib.player.configure import get_players_from_file
from resources.lib.addon.constants import PLAYERS_PRIORITY
from string import Formatter
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


def resolve_to_dummy(handle=None):
    """
    Kodi does 5x retries to resolve url if isPlayable property is set - strm files force this property.
    However, external plugins might not resolve directly to URL and instead might require PlayMedia.
    Also, if external plugin endpoint is a folder we need to do ActivateWindow/Container.Update instead.
    Passing False to setResolvedUrl doesn't work correctly and the retry is triggered anyway.
    In these instances we use a hack to avoid the retry by first resolving to a dummy file instead.
    """
    if handle is None:
        return

    # Set our dummy resolved url
    path = '{}/resources/dummy.mp4'.format(ADDONPATH)
    kodi_log(['lib.player.players - attempt to resolve dummy file\n', path], 1)
    xbmcplugin.setResolvedUrl(handle, True, ListItem(path=path).get_listitem())
    xbmc_monitor, xbmc_player = xbmc.Monitor(), xbmc.Player()

    # Wait till our file plays before stopping it
    timeout = 5
    while (
            not xbmc_monitor.abortRequested()
            and (not xbmc_player.isPlaying() or not xbmc_player.getPlayingFile().endswith('dummy.mp4'))
            and timeout > 0):
        xbmc_monitor.waitForAbort(0.1)
        timeout -= 0.1
    xbmc.Player().stop()
    if timeout <= 0:
        kodi_log(['lib.player.players - resolving dummy file timeout\n', path], 1)
        return -1

    # Wait till our file stops playing before continuing
    timeout = 5
    while (
            not xbmc_monitor.abortRequested()
            and xbmc_player.isPlaying()
            and timeout > 0):
        xbmc_monitor.waitForAbort(0.1)
        timeout -= 0.1
    if timeout <= 0:
        kodi_log(['lib.player.players - stopping dummy file timeout\n', path], 1)
        return -1

    # Clean-up
    del xbmc_monitor
    del xbmc_player
    kodi_log(['lib.player.players -- successfully resolved dummy file\n', path], 1)


class Players(object):
    def __init__(self, tmdb_type, tmdb_id=None, season=None, episode=None, ignore_default=False, **kwargs):
        with busy_dialog():
            self.players = get_players_from_file()
            self.details = get_item_details(tmdb_type, tmdb_id, season, episode)
            self.item = get_detailed_item(tmdb_type, tmdb_id, season, episode, details=self.details) or {}
            self.playerstring = get_playerstring(tmdb_type, tmdb_id, season, episode, details=self.details)
            self.dialog_players = self._get_players_for_dialog(tmdb_type)
            self.default_player = ADDON.getSettingString('default_player_movies') if tmdb_type == 'movie' else ADDON.getSettingString('default_player_episodes')
            self.ignore_default = ignore_default

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
            'is_resolvable': value.get('is_resolvable'),
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
        for k, v in sorted(viewitems(self.players), key=lambda i: try_int(i[1].get('priority')) or PLAYERS_PRIORITY):
            if v.get('disabled', '').lower() == 'true':
                continue  # Skip disabled players
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
        if self.ignore_default:
            return
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
        if path and isinstance(path, tuple):
            return {
                'url': path[0],
                'is_folder': 'true' if path[1] else 'false',
                'isPlayable': 'false' if path[1] else 'true',
                'is_resolvable': player['is_resolvable'] if player.get('is_resolvable') else 'select',
                'player_name': player.get('name')}

    def get_resolved_path(self, return_listitem=True):
        if not self.item:
            return
        get_property('PlayerInfoString', clear_property=True)
        path = self._get_resolved_path(allow_default=True) or {}
        if return_listitem:
            self.details.params = {}
            self.details.path = path.pop('url', None)
            for k, v in viewitems(path):
                self.details.infoproperties[k] = v
            path = self.details.get_listitem()
        return path

    def _update_listing_hack(self, folder_path=None, reset_focus=None):
        """
        Some plugins use container.update after search results to rewrite path history
        This is a quick hack to rewrite the path back to our original path before updating
        """
        if not folder_path:
            return
        xbmc.Monitor().waitForAbort(2)
        container_folderpath = xbmc.getInfoLabel("Container.FolderPath")
        if container_folderpath == folder_path:
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

    def play(self, folder_path=None, reset_focus=None, handle=None):
        # Get some info about current container for container update hack
        if not folder_path:
            folder_path = xbmc.getInfoLabel("Container.FolderPath")
        if not reset_focus and folder_path:
            containerid = xbmc.getInfoLabel("System.CurrentControlID")
            current_pos = xbmc.getInfoLabel("Container({}).CurrentItem".format(containerid))
            reset_focus = 'SetFocus({},{},absolute)'.format(containerid, try_int(current_pos) - 1)

        # Get the resolved path
        listitem = self.get_resolved_path()
        path = listitem.getPath()
        is_folder = True if listitem.getProperty('is_folder') == 'true' else False
        is_resolvable = listitem.getProperty('is_resolvable')

        # Reset folder hack
        self._update_listing_hack(folder_path=folder_path, reset_focus=reset_focus)

        # Check we have an actual path to open
        if not path or path == PLUGINPATH:
            # if handle and handle != -1:
            #     resolve_to_dummy(handle)
            return

        action = None
        if is_folder:
            action = format_folderpath(path)
        elif path.endswith('.strm') or not handle or is_resolvable == 'false':
            action = u'RunScript(plugin.video.themoviedb.helper,play_media={})'.format(path)
        elif is_resolvable == 'select' and xbmcgui.Dialog().yesno(
                '{} - {}'.format(listitem.getProperty('player_name'), ADDON.getLocalizedString(32324)),
                ADDON.getLocalizedString(32325),
                yeslabel='PlayMedia', nolabel='setResolvedUrl'):
            action = u'RunScript(plugin.video.themoviedb.helper,play_media={})'.format(path)

        # Set our playerstring for player monitor to update kodi watched status
        if not is_folder and self.playerstring:
            get_property('PlayerInfoString', set_property=self.playerstring)

        # Kodi launches busy dialog on home screen that needs to be told to close
        # Otherwise the busy dialog will prevent window activation for folder path
        xbmc.executebuiltin('Dialog.Close(busydialog)')

        # Call as builtin for opening folder or playing strm via PlayMedia()
        if action:
            resolve_to_dummy(handle)  # If we're calling external we need to resolve to dummy
            xbmc.executebuiltin(try_encode(try_decode(action)))
            kodi_log(['lib.player - finished executing action\n', action], 1)
            return

        # Else resolve to file directly
        xbmcplugin.setResolvedUrl(handle, True, listitem)
        kodi_log(['lib.player - finished resolving path to url\n', path], 1)

        # Send playable urls to xbmc.Player() not PlayMedia() so we can play as detailed listitem.
        # xbmc.Player().play(path, listitem)
        # kodi_log(['Finished executing Player().Play\n', path], 1)
