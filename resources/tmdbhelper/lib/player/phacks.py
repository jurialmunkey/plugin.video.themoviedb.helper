from xbmc import Monitor, Player
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_setting, executebuiltin, get_infolabel
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.logger import kodi_log


class PlayerHacks():

    @staticmethod
    def wait_for_player_hack(to_start=None, timeout=5, poll=0.25, stop_after=0):
        xbmc_monitor, xbmc_player = Monitor(), Player()
        while (
                not xbmc_monitor.abortRequested()
                and timeout > 0
                and (
                    (to_start and (not xbmc_player.isPlaying() or (isinstance(to_start, str) and not xbmc_player.getPlayingFile().endswith(to_start))))
                    or (not to_start and xbmc_player.isPlaying()))):
            xbmc_monitor.waitForAbort(poll)
            timeout -= poll

        # Wait to stop file
        if timeout > 0 and to_start and stop_after:
            xbmc_monitor.waitForAbort(stop_after)
            if xbmc_player.isPlaying() and xbmc_player.getPlayingFile().endswith(to_start):
                xbmc_player.stop()
        return timeout

    @staticmethod
    def update_listing_hack(folder_path=None, reset_focus=None):
        """
        Some plugins use container.update after search results to rewrite path history
        This is a quick hack to rewrite the path back to our original path before updating
        """
        if not folder_path:
            return
        xbmc_monitor = Monitor()
        xbmc_monitor.waitForAbort(2)
        container_folderpath = get_infolabel("Container.FolderPath")
        if container_folderpath == folder_path:
            return
        executebuiltin(f'Container.Update({folder_path},replace)')
        if not reset_focus:
            return
        timeout = 20
        while not xbmc_monitor.abortRequested() and get_infolabel("Container.FolderPath") != folder_path and timeout > 0:
            xbmc_monitor.waitForAbort(0.25)
            timeout -= 1
        executebuiltin(reset_focus)
        xbmc_monitor.waitForAbort(0.5)

    @staticmethod
    def resolve_to_dummy_hack(handle=None, stop_after=1, delay_wait=0):
        """
        Kodi does 5x retries to resolve url if isPlayable property is set - strm files force this property.
        However, external plugins might not resolve directly to URL and instead might require PlayMedia.
        Also, if external plugin endpoint is a folder we need to do ActivateWindow/Container.Update instead.
        Passing False to setResolvedUrl doesn't work correctly and the retry is triggered anyway.
        In these instances we use a hack to avoid the retry by first resolving to a dummy file instead.
        """
        # If we don't have a handle there's nothing to resolve
        if handle is None:
            return

        # Set our dummy resolved url
        path = f'{ADDONPATH}/resources/dummy.mp4'
        kodi_log(['lib.player.players - attempt to resolve dummy file\n', path], 1)
        from xbmcplugin import setResolvedUrl
        setResolvedUrl(handle, True, ListItem(path=path).get_listitem())

        # Wait till our file plays and then stop after setting duration
        if PlayerHacks.wait_for_player_hack(to_start='dummy.mp4', stop_after=stop_after) <= 0:
            kodi_log(['lib.player.players - resolving dummy file timeout\n', path], 1)
            return -1

        # Wait for our file to stop before continuing
        if stop_after and PlayerHacks.wait_for_player_hack() <= 0:
            kodi_log(['lib.player.players - stopping dummy file timeout\n', path], 1)
            return -1

        # Added delay
        from tmdbhelper.lib.addon.dialog import BusyDialog
        with BusyDialog(False if delay_wait < 1 else True):
            Monitor().waitForAbort(delay_wait)

        # Success
        kodi_log(['lib.player.players -- successfully resolved dummy file\n', path], 1)

    @staticmethod
    def force_recache_kodidb_hack():
        if not get_setting('force_recache_kodidb'):
            return
        from tmdbhelper.lib.script.method.maintenance import recache_kodidb
        recache_kodidb(notification=False)

    @staticmethod
    def playmedia_rerouteplay_hack(action, listitem):
        if get_setting('force_xbmcplayer'):
            kodi_log([f'lib.player - playing path with xbmc.Player():\n', listitem.getPath()], 1)
            Player().play(action, listitem)
            return
        kodi_log([f'lib.player - playing path with PlayMedia():\n', listitem.getPath()], 1)
        action = f'"{action}"' if ',' in action else action
        executebuiltin(f'PlayMedia({action},playlist_type_hint=1)')
