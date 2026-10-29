from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from threading import Event
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_timedelta, set_timestamp
from tmdbhelper.lib.calendar.discover import CalendarDiscoverCache, MovieCalendarDiscoverCache
from tmdbhelper.lib.calendar.progress import CalendarFetchProgress


class CalendarDataGetter:
    """Configured range with an exclusive end date and Discover request filters."""
    tmdb_type = 'tv'
    filters = None
    progress_callback = None
    max_workers = CalendarDiscoverCache.max_workers
    day_workers = 4

    @cached_property
    def discover(self):
        return self.get_discover()

    def get_discover(self):
        discover = {'tv': CalendarDiscoverCache, 'movie': MovieCalendarDiscoverCache}[self.tmdb_type]()
        discover.filters = self.filters or {}
        return discover

    @cached_property
    def dates(self):
        return self.get_dates()

    def get_dates(self):
        start = convert_timestamp(self.start_date, time_fmt='%Y-%m-%d')
        end = convert_timestamp(self.end_date, time_fmt='%Y-%m-%d')
        return [(start + get_timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end - start).days)]

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        self.fetch_days()
        rows = self.discover.database.get_days(
            start_date=self.start_date, end_date=self.end_date,
            current_time=set_timestamp(0, set_int=True), **self.discover.cache_parameters)
        return [dict(row) for row in rows]

    def get_day_discover(self, progress, cancel_event):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        discover = self.get_discover()
        discover.database = self.discover.database
        discover.tmdb_api = TMDb(
            api_key=self.discover.tmdb_api.api_key,
            language=self.discover.tmdb_api.language)
        discover.max_workers = self.max_workers
        discover.progress_callback = progress.report
        discover.cancel_event = cancel_event
        return discover

    @staticmethod
    def wait_for_days(futures, progress):
        pending = set(futures)
        while pending:
            finished, pending = wait(pending, timeout=0.1, return_when=FIRST_COMPLETED)
            progress.drain()
            for future in finished:
                future.result()
        progress.drain()

    def fetch_days(self):
        if not self.dates:
            return
        progress = CalendarFetchProgress(self.dates, self.progress_callback)
        cancel_event = Event()
        workers = [self.get_day_discover(progress, cancel_event) for date in self.dates]
        with ThreadPoolExecutor(max_workers=min(self.day_workers, len(self.dates))) as pool:
            futures = [pool.submit(worker.get_day, date) for worker, date in zip(workers, self.dates)]
            try:
                self.wait_for_days(futures, progress)
            finally:
                cancel_event.set()
                for future in futures:
                    future.cancel()
