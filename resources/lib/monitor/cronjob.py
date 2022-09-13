from xbmc import Monitor
from tmdbhelper.parser import try_int
from threading import Thread
from resources.lib.addon.tmdate import convert_timestamp, get_datetime_now, get_timedelta, get_datetime_today, get_datetime_time, get_datetime_combine
from resources.lib.addon.plugin import get_setting, executebuiltin, get_infolabel, ADDONPATH


def clean_old_databases():
    """ Once-off routine to delete old unused database versions to avoid wasting disk space """
    from resources.lib.files.futils import delete_folder
    for f in ['database', 'database_v2', 'database_v3', 'database_v4']:
        delete_folder(f, force=True, check_exists=True)


def mem_cache_kodidb(notification=True):
    from resources.lib.api.kodi.rpc import KodiLibrary
    from resources.lib.addon.logger import TimerFunc
    from xbmcgui import Dialog
    with TimerFunc('KodiLibrary sync took', inline=True):
        KodiLibrary('movie', cache_refresh=True)
        KodiLibrary('tvshow', cache_refresh=True)
        if notification:
            Dialog().notification('TMDbHelper', 'Kodi Library cached to memory', icon=f'{ADDONPATH}/icon.png')


class CronJobMonitor(Thread):
    def __init__(self, update_hour=0):
        Thread.__init__(self)
        self.exit = False
        self.poll_time = 1800  # Poll every 30 mins since we don't need to get exact time for update
        self.update_hour = update_hour
        self.xbmc_monitor = Monitor()

    def run(self):
        clean_old_databases()
        mem_cache_kodidb(notification=False)

        self.xbmc_monitor.waitForAbort(600)  # Wait 10 minutes before doing updates to give boot time
        if self.xbmc_monitor.abortRequested():
            del self.xbmc_monitor
            return

        self.next_time = get_datetime_combine(get_datetime_today(), get_datetime_time(try_int(self.update_hour)))  # Get today at hour
        self.last_time = get_infolabel('Skin.String(TMDbHelper.AutoUpdate.LastTime)')  # Get last update
        self.last_time = convert_timestamp(self.last_time) if self.last_time else None
        if self.last_time and self.last_time > self.next_time:
            self.next_time += get_timedelta(hours=24)  # Already updated today so set for tomorrow

        while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
            if get_setting('library_autoupdate'):
                if get_datetime_now() > self.next_time:  # Scheduled time has past so lets update
                    executebuiltin('RunScript(plugin.video.themoviedb.helper,library_autoupdate)')
                    executebuiltin(f'Skin.SetString(TMDbHelper.AutoUpdate.LastTime,{get_datetime_now().strftime("%Y-%m-%dT%H:%M:%S")})')
                    self.next_time += get_timedelta(hours=24)  # Set next update for tomorrow
            self.xbmc_monitor.waitForAbort(self.poll_time)

        del self.xbmc_monitor
