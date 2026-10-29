import hashlib
import json
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from jurialmunkey.ftools import cached_property
from jurialmunkey.locker import MutexPropLock
from tmdbhelper.lib.addon.consts import DAY_IN_SECONDS
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_datetime_today, set_timestamp
from tmdbhelper.lib.calendar.database import CalendarDatabase
from tmdbhelper.lib.calendar.pages import CalendarPageFetcher


class CalendarDiscoverCache:
    """Cache complete Discover days independently of library membership."""
    tmdb_type = 'tv'
    date_filter = 'air_date'
    filters = {}
    progress_callback = None
    max_workers = 10
    cancel_event = None

    def report_progress(self, date, status, page=0, pages=0):
        if self.progress_callback:
            self.progress_callback(date, status, page, pages)

    @cached_property
    def database(self):
        return CalendarDatabase()

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def cache_parameters(self):
        return self.get_cache_parameters()

    def get_cache_parameters(self):
        filters = {
            key: value for key, value in self.request_filters.items()
            if key not in ('timezone', 'language', 'include_adult', 'sort_by')
        }
        return {
            'tmdb_type': self.tmdb_type,
            'timezone': self.request_filters['timezone'],
            'language': self.request_filters['language'],
            'filters': json.dumps(filters, sort_keys=True, separators=(',', ':')),
        }

    @cached_property
    def request_filters(self):
        return self.get_request_filters()

    def get_request_filters(self):
        return dict(
            self.filters, timezone='UTC', include_adult='false',
            language=self.tmdb_api.req_language, sort_by='popularity.desc')

    def get_expiry_days(self, date):
        offset = (convert_timestamp(date, time_fmt='%Y-%m-%d').date() - get_datetime_today().date()).days
        if offset < -1:
            return 14
        return {-1: 7, 0: 3, 1: 2}.get(offset, 1)

    def get_response(self, date, page, tmdb_api=None):
        if self.cancel_event is not None and self.cancel_event.is_set():
            raise CancelledError('Calendar download cancelled')
        tmdb_api = tmdb_api or self.tmdb_api
        return tmdb_api.get_response_json(
            'discover', self.tmdb_type, **dict(self.request_filters, **{
                f'{self.date_filter}.gte': date,
                f'{self.date_filter}.lte': date,
                'page': page,
            }))

    def get_uncached_day(self, date):
        first = self.get_response(date, 1)
        pages = first['total_pages']
        if pages > 500:
            raise RuntimeError(f'TMDb calendar {date} exceeds the Discover pagination limit')
        items = {item['id'] for item in first['results']}
        self.report_progress(date, 'page', 1, max(pages, 1))
        if pages > 1:
            items.update(self.get_remaining_page_ids(date, pages))
        kodi_log(f'Calendar: fetched {date} ({max(pages, 1)} pages, {len(items)} shows)', 1)
        return sorted(items)

    def get_remaining_page_ids(self, date, pages):
        fetcher = CalendarPageFetcher(self, date)
        items = set()
        with ThreadPoolExecutor(max_workers=min(self.max_workers, pages - 1)) as pool:
            futures = [pool.submit(fetcher.get_page, page) for page in range(2, pages + 1)]
            try:
                for completed, future in enumerate(as_completed(futures), 2):
                    items.update(future.result())
                    self.report_progress(date, 'page', completed, pages)
            finally:
                for future in futures:
                    future.cancel()
        return items

    def get_day(self, date):
        self.report_progress(date, 'checking')
        lock_key = json.dumps((self.cache_parameters, date), sort_keys=True)
        lock_id = hashlib.sha256(lock_key.encode()).hexdigest()
        with MutexPropLock(f'Database.Calendar.{lock_id}', timeout=600, kodi_log=kodi_log):
            items = self.database.get_day(
                date=date, current_time=set_timestamp(0, set_int=True), **self.cache_parameters)
            if items is not None:
                self.report_progress(date, 'cached')
                return items
            items = self.get_uncached_day(date)
            fetched_at = set_timestamp(0, set_int=True)
            self.database.set_day(
                date=date, expiry=fetched_at + self.get_expiry_days(date) * DAY_IN_SECONDS,
                items=items, **self.cache_parameters)
            self.report_progress(date, 'complete')
            return items


class MovieCalendarDiscoverCache(CalendarDiscoverCache):
    tmdb_type = 'movie'
    date_filter = 'primary_release_date'
