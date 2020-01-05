# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import threading
import resources.lib.utils as utils
from resources.lib.downloader import Downloader
from resources.lib.traktapi import TraktAPI
from resources.lib.plugin import Plugin
from resources.lib.player import Player
from resources.lib.service import ServiceMonitor


ID_VIDEOINFO = 12003


class Script(Plugin):
    def __init__(self):
        super(Script, self).__init__()
        self.home = xbmcgui.Window(10000)
        self.params = {}
        self.first_run = True
        self.added_path = None
        self.prefixpath = '{0}Path.'.format(self.prefixname)
        self.prefixlock = '{0}Locked'.format(self.prefixname)
        self.prefixcurrent = '{0}Current'.format(self.prefixpath)
        self.prefixposition = '{0}Position'.format(self.prefixname)
        self.prefixinstance = '{0}Instance'.format(self.prefixname)
        self.monitor = xbmc.Monitor()

    def get_params(self):
        for arg in sys.argv:
            if arg == 'script.py':
                pass
            elif '=' in arg:
                arg_split = arg.split('=', 1)
                if arg_split[0] and arg_split[1]:
                    key, value = arg_split
                    self.params.setdefault(key, value)
            else:
                self.params.setdefault(arg, True)

    def get_position(self):
        position = self.home.getProperty(self.prefixposition)
        return utils.try_parse_int(position)

    def reset_props(self):
        self.position = 0
        self.added_path = None
        self.unlock_path()
        self.home.clearProperty(self.prefixcurrent)
        self.home.clearProperty(self.prefixposition)
        self.home.clearProperty('{0}0'.format(self.prefixpath))
        self.home.clearProperty('{0}1'.format(self.prefixpath))

    def set_props(self, position=1, path=''):
        self.added_path = path
        self.home.setProperty(self.prefixcurrent, path)
        self.home.setProperty('{0}{1}'.format(self.prefixpath, position), path)
        self.home.setProperty(self.prefixposition, str(position))

    def lock_path(self, condition):
        if not condition:
            self.unlock_path()
            return
        self.home.setProperty(self.prefixlock, 'True')

    def unlock_path(self):
        self.home.clearProperty(self.prefixlock)

    def get_instance(self, call_id=None):
        return False if call_id and not xbmc.getCondVisibility("Window.IsVisible({})".format(call_id)) else True

    def wait_for_property(self, property, value=None, setproperty=False, poll=1, timeout=10):
        """
        Waits until property matches value. None value waits for property to be cleared.
        Will set property to value if setproperty flag is set. None value clears property.
        Returns True when successful.
        """
        if setproperty and value:
            self.home.setProperty(property, value)
        elif setproperty and not value:
            self.home.clearProperty(property)

        t = 0
        is_property = True if (
            (not value and not self.home.getProperty(property)) or
            (value and self.home.getProperty(property) == value)) else False

        while not self.monitor.abortRequested() and t < timeout and not is_property:
            self.monitor.waitForAbort(poll)
            is_property = True if (
                (not value and not self.home.getProperty(property)) or
                (value and self.home.getProperty(property) == value)) else False
            t += poll

        return is_property

    def wait_for_id(self, to_close=False, window_id=None, call_id=None, poll=1, timeout=30):
        """
        Waits for matching ID to open before continuing
        Set to_close flag to wait for matching ID to close instead
        Returns True if successful.

        """
        if not window_id:
            return True

        t = 0
        is_instance = self.get_instance(call_id)
        is_visible = xbmc.getCondVisibility("Window.IsVisible({})".format(window_id))

        while (
                not self.monitor.abortRequested() and t < timeout and is_instance and
                ((to_close and is_visible) or (not to_close and not is_visible))):
            self.monitor.waitForAbort(poll)
            is_instance = self.get_instance(call_id)
            is_visible = xbmc.getCondVisibility("Window.IsVisible({})".format(window_id))
            t += poll

        return True if is_instance and t < timeout else False

    def wait_for_update(self, call_id=None, poll=1, timeout=60):
        """
        Wait for container to update.
        Returns True if successful
        """
        is_instance = self.get_instance(call_id)
        is_updating = xbmc.getCondVisibility("Container(9999).IsUpdating")
        num_items = utils.try_parse_int(xbmc.getInfoLabel("Container(9999).NumItems"))

        t = 0
        while not self.monitor.abortRequested() and t < timeout and is_instance and (is_updating or not num_items):
            self.monitor.waitForAbort(poll)
            is_instance = self.get_instance(call_id)
            is_updating = xbmc.getCondVisibility("Container(9999).IsUpdating")
            num_items = utils.try_parse_int(xbmc.getInfoLabel("Container(9999).NumItems"))
            t += poll

        return True if is_instance and t < timeout else False

    def call_service(self):
        call_id = utils.try_parse_int(self.params.get('call_auto'))
        kodi_id = call_id + 10000 if call_id < 10000 else call_id  # Convert to Kodi ID in 10000 range
        my_call_id = None if self.first_run else call_id

        # Close info dialogs if still open
        if xbmc.getCondVisibility('Window.IsVisible({})'.format(ID_VIDEOINFO)):
            xbmc.executebuiltin('Dialog.Close({})'.format(ID_VIDEOINFO))
            if not self.wait_for_id(to_close=True, window_id=ID_VIDEOINFO, call_id=my_call_id):
                return self.call_reset()  # Clear and exit if timeout or user closed base window

        # If we're at 0 then close and exit
        if self.get_position() == 0:
            xbmc.executebuiltin('Action(Back)')
            return self.call_reset()  # Clear and exit

        # Open our call_id window if first run
        if self.first_run:
            xbmc.executebuiltin('ActivateWindow({})'.format(call_id))
            if not self.wait_for_id(window_id=call_id, poll=0.5):
                return self.call_reset()  # Clear and exit if timeout
        window = xbmcgui.Window(kodi_id)

        # Check that list 9999 exists
        controllist = window.getControl(9999)
        if not controllist:
            utils.kodi_log('SKIN ERROR!\nList control 9999 not available in Window {0}'.format(call_id), 1)
            return self.call_reset()  # Clear and exit if timeout or user closed base window
        controllist.reset()

        # Wait until container updates
        self.monitor.waitForAbort(1)
        if not self.wait_for_update(call_id=call_id):
            return self.call_reset()  # Clear and exit if timeout or user closed base window

        # Open info dialog
        window.setFocus(controllist)
        xbmc.executebuiltin('SetFocus(9999,0,absolute)')
        xbmc.executebuiltin('Action(Info)')
        if not self.wait_for_id(window_id=ID_VIDEOINFO, call_id=call_id):
            return self.call_reset()  # Clear and exit if timeout or user closed base window

        # Wait for action
        func = None
        while not self.monitor.abortRequested() and not func:
            current_path = self.home.getProperty(self.prefixcurrent)
            if not xbmc.getCondVisibility("Window.IsVisible({})".format(call_id)):
                func = self.call_reset  # User closed out everything so let's do the nuclear option
            elif not xbmc.getCondVisibility("Window.IsVisible({})".format(ID_VIDEOINFO)):
                func = self.call_previous  # Dialog closed so we should delete the path and call loopback
            elif self.added_path != current_path:
                self.added_path = current_path
                func = self.call_service  # New path added so call loopback
            self.monitor.waitForAbort(0.5)  # Poll every X
        self.first_run = False
        func()

    def close_dialog(self):
        self.reset_props()
        xbmc.executebuiltin('Dialog.Close({})'.format(ID_VIDEOINFO))
        close_id = utils.try_parse_int(self.params.get('close_dialog'))
        if not close_id:
            return
        close_id = close_id + 10000 if close_id < 10000 else close_id
        try:
            xbmcgui.Window(close_id).close()
        except Exception as exc:
            utils.kodi_log(exc, 1)

    def call_reset(self):
        self.reset_props()
        self.home.clearProperty(self.prefixinstance)

    def call_previous(self):
        self.prev_path()
        self.call_service()

    def call_auto(self):
        # If call_auto not set then use old method
        if not self.params.get('call_auto'):
            self.call_window()
            return

        # Get call_auto window ID and make sure it is a custom window.
        call_id = utils.try_parse_int(self.params.get('call_auto'))
        if not call_id:
            return

        # Check if already running
        if xbmc.getCondVisibility("Window.IsVisible({})".format(call_id)):
            return  # Window already open so must already be running let's exit since we added our paths
        elif self.home.getProperty(self.prefixinstance):
            self.reset_props()  # Window not open but instance set so let's reset everything
            self.home.clearProperty(self.prefixinstance)  # TODO: Kill old instances
            self.router()
        else:  # Window not open and instance not set so let's start our service
            self.home.setProperty(self.prefixinstance, 'True')
            self.call_service()

    def call_window(self):
        xbmc.executebuiltin('Dialog.Close({})'.format(ID_VIDEOINFO))
        if self.params.get('call_id'):
            xbmc.executebuiltin('ActivateWindow({0})'.format(self.params.get('call_id')))
        elif self.params.get('call_path'):
            xbmc.executebuiltin('ActivateWindow(videos, {0}, return)'.format(self.params.get('call_path')))
        elif self.params.get('call_update'):
            xbmc.executebuiltin('Container.Update({0})'.format(self.params.get('call_update')))

    def add_path(self):
        url = self.params.get('add_path', '')
        url = url.replace('info=play', 'info=details')
        url = url.replace('info=seasons', 'info=details')
        url = '{0}&{1}'.format(url, 'extended=True') if 'extended=True' not in url else url
        self.position = self.get_position() + 1
        self.set_props(self.position, url)
        self.lock_path(self.params.get('prevent_del'))
        self.call_auto()

    def add_query(self):
        with utils.busy_dialog():
            query = utils.try_decode_string(self.params.get('add_query', ''))
            item = utils.dialog_select_item(query)
            if not item:
                return
            tmdb_id = self.tmdb.get_tmdb_id(self.params.get('type'), query=item, selectdialog=True)
            if tmdb_id:
                self.position = self.get_position() + 1
                url = 'plugin://plugin.video.themoviedb.helper/?info=details&amp;type={0}&amp;tmdb_id={1}'.format(self.params.get('type'), tmdb_id)
                self.set_props(self.position, url)
                self.lock_path(self.params.get('prevent_del'))
            else:
                utils.kodi_log('Unable to find TMDb ID!\nQuery: {0} Type: {1}'.format(self.params.get('add_query'), self.params.get('type')), 1)
                return
        self.call_auto()

    def add_prop(self):
        item = utils.dialog_select_item(self.params.get('add_prop'))
        if not item:
            return
        prop_name = '{0}{1}'.format(self.prefixname, self.params.get('prop_id'))
        self.home.setProperty(prop_name, item)
        self.call_auto()

    def prev_path(self):
        # Get current position and clear it
        self.position = self.get_position()
        self.home.clearProperty('{0}{1}'.format(self.prefixpath, self.position))

        # If it was first position then let's clear everything
        if not self.position > 1:
            self.reset_props()
            return

        # Otherwise set previous position to current position
        self.position -= 1
        path = self.home.getProperty('{0}{1}'.format(self.prefixpath, self.position))
        self.set_props(self.position, path)

    def del_path(self):
        if self.home.getProperty(self.prefixlock):
            self.added_path = None
            self.unlock_path()
            return

        self.prev_path()
        self.call_window()

    def play(self):
        utils.kodi_log('Script -- Attempting to play item:\n{0}'.format(self.params), 2)
        if not self.params.get('play') or not self.params.get('tmdb_id'):
            return
        Player().play(
            itemtype=self.params.get('play'), tmdb_id=self.params.get('tmdb_id'),
            season=self.params.get('season'), episode=self.params.get('episode'))

    def update_players(self):
        players_url = self.addon.getSettingString('players_url')
        players_url = xbmcgui.Dialog().input('Enter URL to download players', defaultt=players_url)
        if not xbmcgui.Dialog().yesno('Download Players', 'Download players from URL?\n[B]{0}[/B]'.format(players_url)):
            return
        self.addon.setSettingString('players_url', players_url)
        downloader = Downloader(
            extract_to='special://profile/addon_data/plugin.video.themoviedb.helper/players',
            download_url=players_url)
        downloader.get_extracted_zip()

    def set_defaultplayer(self):
        player = Player()
        tmdbtype = self.params.get('set_defaultplayer')
        setting = 'default_player_episodes' if tmdbtype == 'tv' else 'default_player_{0}s'.format(tmdbtype)
        player.setup_players(tmdbtype=tmdbtype, clearsetting=True)
        idx = xbmcgui.Dialog().select(
            'Choose Default Player for {0}'.format(utils.type_convert(tmdbtype, 'plural')), player.itemlist)
        if idx == 0:
            self.addon.setSetting(setting, '')
        if idx > 0:
            selected = player.itemlist[idx].getLabel()
            self.addon.setSetting(setting, selected)

    def clear_defaultplayers(self):
        self.addon.setSetting('default_player_movies', '')
        self.addon.setSetting('default_player_episodes', '')

    def restart_service(self):
        if self.home.getProperty('TMDbHelper.ServiceStarted') == 'True':
            self.wait_for_property('TMDbHelper.ServiceStop', value='True', setproperty=True)  # Stop service
        self.wait_for_property('TMDbHelper.ServiceStop', value=None)  # Wait until Service clears property
        t = threading.Thread(target=ServiceMonitor)
        t.start()  # Start our service monitor thread

    def router(self):
        if not self.params:
            """ If no params assume user wants to run plugin """
            # TODO: Maybe restart service here too?
            self.params = {'call_path': 'plugin://plugin.video.themoviedb.helper/'}
        if self.params.get('authenticate_trakt'):
            TraktAPI(force=True)
        elif self.params.get('update_players'):
            self.update_players()
        elif self.params.get('set_defaultplayer'):
            self.set_defaultplayer()
        elif self.params.get('clear_defaultplayers'):
            self.clear_defaultplayers()
        elif self.params.get('add_path'):
            self.add_path()
        elif self.params.get('add_query') and self.params.get('type'):
            self.add_query()
        elif self.params.get('add_prop') and self.params.get('prop_id'):
            self.add_prop()
        elif self.params.get('del_path'):
            self.del_path()
        elif self.params.get('close_dialog'):
            self.close_dialog()
        elif self.params.get('reset_path'):
            self.reset_props()
        elif self.params.get('play'):
            self.play()
        elif self.params.get('restart_service'):
            self.restart_service()
        else:
            self.call_window()
