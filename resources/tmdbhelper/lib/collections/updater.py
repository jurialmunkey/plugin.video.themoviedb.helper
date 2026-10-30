"""Budgeted background updates for a profile-local collection index."""
from contextlib import closing
from datetime import datetime, timedelta, timezone
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from tmdbhelper.lib.collections.client import (
    CollectionClient, CollectionAPIError, RequestBudgetExceeded, get_utc_timestamp)
from tmdbhelper.lib.collections.runtime_database import RuntimeCollectionDatabase
import sqlite3


class BudgetedCollectionClient(CollectionClient):
    def __init__(self, api_key, cache_directory, database, daily_limit, abort=None):
        super().__init__(api_key, cache_directory, requests_per_second=1, max_requests=5)
        self.database = database
        self.daily_limit = daily_limit
        self.abort = abort or (lambda: False)
        self.retry_after = None

    def reserve_request(self, details):
        self.check_abort()
        super().reserve_request(details)
        self.check_abort()
        if details:
            self.reserve_daily_request()

    def check_abort(self):
        if self.abort():
            raise RequestBudgetExceeded('Collection maintenance stopped')

    def reserve_daily_request(self):
        day = datetime.now(timezone.utc).astimezone().date().isoformat()
        if not self.database.reserve_request(day, self.daily_limit):
            raise RequestBudgetExceeded('Daily collection request budget exhausted')

    def download(self, url, label, details=False):
        # Client retries are persisted between polls; do not keep Kodi sleeping
        # through a server's Retry-After interval or a series of network failures.
        self.reserve_request(details)
        self.retry_after = None
        request = Request(url, headers={'User-Agent': 'TMDbHelper-Collections'})
        try:
            with urlopen(request, timeout=10) as response:
                return response.read()
        except HTTPError as error:
            self.raise_http_error(error, label)
        except (URLError, TimeoutError, ConnectionError, HTTPException):
            raise CollectionAPIError(f'{label}: connection failed') from None

    def raise_http_error(self, error, label):
        status = error.code
        value = error.headers.get('Retry-After')
        error.close()
        self.retry_after = self.get_retry_timestamp(value, status)
        raise CollectionAPIError(f'{label}: HTTP {status}', status) from None

    def get_retry_timestamp(self, value, status):
        if value is None and status != 429:
            return None
        seconds = self.get_retry_delay(value, 0) if value is not None else 60
        return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


class CollectionUpdater:
    def __init__(self, index, api_key, daily_limit=25, abort=None):
        self.index = index
        self.api_key = api_key
        self.daily_limit = daily_limit
        self.abort = abort or (lambda: False)

    def update_export(self, database, client, now):
        snapshot_date = (now - timedelta(days=1)).date()
        if database.get_metadata('snapshot_date') == snapshot_date.isoformat():
            return
        retry_after = database.get_metadata('export_retry_after')
        if retry_after and retry_after > now.isoformat(timespec='microseconds'):
            return
        try:
            identifiers, digest, size = client.get_export(snapshot_date)
        except CollectionAPIError:
            self.defer_export(database, client, now)
            raise
        database.set_snapshot(identifiers, snapshot_date.isoformat(), digest)
        with database.connection:
            database.set_metadata({'export_retry_after': ''})
        self.prune_exports(client.cache_directory, snapshot_date)

    @staticmethod
    def defer_export(database, client, now):
        retry_after = max((now + timedelta(hours=1)).isoformat(), client.retry_after or '')
        with database.connection:
            database.set_metadata({'export_retry_after': retry_after})

    @staticmethod
    def prune_exports(directory, snapshot_date):
        current = f'collection_ids_{snapshot_date:%m_%d_%Y}.json.gz'
        expired = (filename for filename in directory.glob('collection_ids_*.json.gz') if filename.name != current)
        for filename in expired:
            filename.unlink()

    def run(self):
        if self.abort():
            return
        self.index.initialise()
        try:
            with closing(sqlite3.connect(self.index.filename, timeout=30)) as connection:
                self.run_update(RuntimeCollectionDatabase(connection))
        except RequestBudgetExceeded:
            return

    def get_client(self, database):
        return BudgetedCollectionClient(
            self.api_key, self.index.filename.parent / 'exports', database, self.daily_limit, self.abort)

    def run_update(self, database):
        now = datetime.now(timezone.utc)
        client = self.get_client(database)
        self.update_export(database, client, now)
        if not self.can_update_details(database, now):
            return
        queue = database.get_queue(get_utc_timestamp(), now, due_only=True)
        self.process_queue(database, client, queue)

    def can_update_details(self, database, now):
        retry_after = database.get_metadata('api_retry_after')
        if retry_after and retry_after > now.isoformat(timespec='microseconds'):
            return False
        day = now.astimezone().date().isoformat()
        return database.get_requests_used(day) < self.daily_limit

    def process_queue(self, database, client, queue):
        for collection_id in queue:
            if not self.update_collection(database, client, collection_id):
                break

    def update_collection(self, database, client, collection_id):
        try:
            movies = client.get_collection(collection_id)
        except CollectionAPIError as error:
            return self.handle_collection_error(database, client, collection_id, error)
        except (ValueError, KeyError, TypeError) as error:
            database.set_failure(collection_id, get_utc_timestamp(), None)
            raise ValueError(f'Collection {collection_id}: invalid source data: {error}') from error
        database.set_collection(collection_id, movies, get_utc_timestamp())
        return True

    @staticmethod
    def handle_collection_error(database, client, collection_id, error):
        database.set_failure(collection_id, get_utc_timestamp(), error.status)
        if client.retry_after:
            database.defer_retry(collection_id, client.retry_after)
            return False
        if error.status in (401, 403):
            raise error
        return True
