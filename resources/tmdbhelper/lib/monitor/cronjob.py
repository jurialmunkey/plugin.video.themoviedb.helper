from xbmc import Monitor
from jurialmunkey.parser import try_int
from threading import Thread
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_datetime_now, get_timedelta, get_datetime_today, get_datetime_time, get_datetime_combine
from tmdbhelper.lib.addon.plugin import get_setting, executebuiltin, get_infolabel
from tmdbhelper.lib.script.method import mem_cache_kodidb, clean_old_databases


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
