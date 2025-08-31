from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_setting, executebuiltin
from tmdbhelper.lib.addon.logger import kodi_log


class PlayerHacksResolvedURL:

    """
    Kodi does 5x retries to resolve url if isPlayable property is set - strm files force this property.
    However, external plugins might not resolve directly to URL and instead might require PlayMedia.
    Also, if external plugin endpoint is a folder we need to do ActivateWindow/Container.Update instead.
    Passing False to setResolvedUrl doesn't work correctly and the retry is triggered anyway.
    In these instances we use a hack to avoid the retry by first resolving to a dummy file instead.
    """

    dummy_filename = 'dummy.mp4'
    dummy_listitem_path = f'{ADDONPATH}/resources/dummy.mp4'
    poll_wait = 0.25

    def __init__(self, listitem, action=None, handle=None, f_strm=False, equeue=None):
        self.listitem = listitem
        self.action = action
        self.handle = handle  # Handle from plugin
        self.f_strm = f_strm  # Filepath is strm file
        self.equeue = equeue  # Function to run after playback to queue more episodes

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    @cached_property
    def xbmc_player(self):
        from xbmc import Player
        return Player()

    @cached_property
    def dummy_duration(self):
        from jurialmunkey.parser import try_float
        return try_float(get_setting('dummy_duration', 'str')) or 1.0

    @cached_property
    def dummy_delay(self):
        from jurialmunkey.parser import try_float
        return try_float(get_setting('dummy_delay', 'str')) or 1.0

    @cached_property
    def listitem_path(self):
        return self.listitem.getPath()

    @cached_property
    def is_folder(self):
        return bool(self.listitem.getProperty('is_folder') == 'true')

    @cached_property
    def dummy_listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(path=self.dummy_listitem_path).get_listitem()

    @cached_property
    def playerstring(self):
        from tmdbhelper.lib.player.details.playerstring import make_playerstring
        playerstring = make_playerstring(self.listitem)
        kodi_log(['lib.player - playerstring:\n', f'{playerstring}'], 1)
        return playerstring

    def update_episodequeue(self):
        try:
            self.equeue()
        except (TypeError, AttributeError):
            return

    def update_playerstring(self):
        from jurialmunkey.window import get_property
        if not self.playerstring:
            return get_property('PlayerInfoString', clear_property=True)
        get_property('PlayerInfoString', set_property=self.playerstring)

    def set_resolved_url(self):
        from xbmcplugin import setResolvedUrl
        kodi_log(['lib.player - resolving path to url\n', self.listitem_path], 1)
        setResolvedUrl(self.handle, True, self.listitem)
        self.update_playerstring()
        self.update_episodequeue()

    def executebuiltin_player(self):
        kodi_log(['lib.player - playing path with xbmc.Player():\n', self.listitem_path], 1)
        self.xbmc_player.play(self.action, self.listitem)
        self.update_playerstring()
        self.update_episodequeue()

    def executebuiltin_action(self):
        kodi_log(['lib.player - executing action:\n', self.action], 1)
        # Kodi launches busy dialog on home screen that needs to be told to close
        # Otherwise the busy dialog will prevent window activation for folder path
        executebuiltin('Dialog.Close(busydialog, force)')
        executebuiltin(self.action)

    def wait_for_player_condition(self, filename=None):
        """
        filename=file to wait for playback of set file
        filename=True to wait for playback of any file
        filename=None to wait for playback to stop
        """
        if not filename:
            return bool(self.xbmc_player.isPlaying())
        if not self.xbmc_player.isPlaying():
            return True
        if isinstance(filename, str):
            return bool(not self.xbmc_player.getPlayingFile().endswith(filename))
        return False

    def wait_for_player(self, filename=None, timeout=5, stop_after=0):
        while (
                not self.xbmc_monitor.abortRequested()
                and timeout > 0
                and self.wait_for_player_condition(filename)
        ):
            self.xbmc_monitor.waitForAbort(self.poll_wait)
            timeout -= self.poll_wait

        # Wait to stop file
        self.player_stop_after(filename, stop_after) if stop_after > 0 else None
        return timeout

    def player_stop_after(self, filename=None, wait=0):
        kodi_log(f'lib.player - wait {wait} to stop {filename}', 1)
        self.xbmc_monitor.waitForAbort(wait)
        if not self.xbmc_player.isPlaying():
            kodi_log(f'lib.player - not playing anything!', 1)
            return
        if not self.xbmc_player.getPlayingFile().endswith(filename):
            kodi_log(f'lib.player - not playing {filename}', 1)
            return
        kodi_log(f'lib.player - stopping {filename}', 1)
        self.xbmc_player.stop()

    def set_resolved_url_dummy(self):
        from xbmcplugin import setResolvedUrl
        kodi_log(['lib.player - resolving dummy path to url\n', self.dummy_listitem_path], 1)
        setResolvedUrl(self.handle, True, self.dummy_listitem)

    def rtd_check_strm(self):
        if not self.f_strm and get_setting('only_resolve_strm'):
            kodi_log(['lib.player - skipped dummy no strm setting\n', self.dummy_filename], 1)
            return False
        return True

    def rtd_check_handle(self):
        if self.handle is None:
            kodi_log(['lib.player - skipped dummy no resolve handle\n', self.dummy_filename], 1)
            return False
        return True

    def rtd_check_action(self):
        if not self.is_folder and not self.action:
            kodi_log(['lib.player - skipped dummy have resolvable file\n', self.dummy_filename], 1)
            return False
        return True

    def rtd_check_start(self):
        # Wait till our dummy file plays and then stop after setting duration
        self.set_resolved_url_dummy()
        if self.wait_for_player(filename=self.dummy_filename, stop_after=self.dummy_duration) <= 0:
            kodi_log(['lib.player - resolve dummy file timeout\n', self.dummy_filename], 1)
            return False
        return True

    def rtd_check_stop(self):
        # Wait for our file to stop before continuing
        if self.dummy_duration and self.wait_for_player() <= 0:
            kodi_log(['lib.player - stopped dummy file timeout\n', self.dummy_filename], 1)
            return False
        return True

    def rtd_success(self):
        # Wait for additional delay after stopping
        from tmdbhelper.lib.addon.dialog import BusyDialog
        with BusyDialog(False if self.dummy_delay < 1 else True):
            self.xbmc_monitor.waitForAbort(self.dummy_delay)
        kodi_log(['lib.player -- successfully resolved dummy file\n', self.dummy_filename], 1)
        return True

    def rtd_run(self):
        for func in (
            self.rtd_check_handle,
            self.rtd_check_action,
            self.rtd_check_strm,
            self.rtd_check_start,
            self.rtd_check_stop,
            self.rtd_success,
        ):
            if not func():
                self.dummy_success = False
                return
        self.dummy_success = True

    @cached_property
    def route(self):
        if self.is_folder:
            return self.executebuiltin_action
        if self.action:
            return self.executebuiltin_player
        return self.set_resolved_url

    def run(self):
        self.rtd_run()
        self.route()
