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
    def force_recache_kodidb_hack():
        if not get_setting('force_recache_kodidb'):
            return
        from tmdbhelper.lib.script.method.maintenance import recache_kodidb
        recache_kodidb(notification=False)
