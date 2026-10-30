"""Standard-library TMDb client for collection-index maintenance."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from pathlib import Path
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import gzip
import hashlib
import json
import os
import time


class CollectionAPIError(RuntimeError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class RequestBudgetExceeded(RuntimeError):
    pass


class CollectionClient:
    attempts = 5
    api_url = 'https://api.themoviedb.org/3'
    export_url = 'https://files.tmdb.org/p/exports'

    def __init__(self, api_key, cache_directory, requests_per_second=10, max_requests=None):
        self.api_key = api_key
        self.cache_directory = Path(cache_directory)
        self.request_interval = 1 / requests_per_second
        self.max_requests = max_requests
        self.detail_requests = 0
        self.export_requests = 0
        self.lock = Lock()
        self.next_request = 0
        self.cooldown_until = 0

    def reserve_request(self, details):
        while True:
            delay = self.get_request_delay(details)
            if delay <= 0:
                return
            # Recheck the shared cooldown after waking; workers must not all
            # issue their preallocated requests together after a 429 pause.
            time.sleep(delay)

    def get_request_delay(self, details):
        with self.lock:
            if details and self.max_requests is not None and self.detail_requests >= self.max_requests:
                raise RequestBudgetExceeded('Collection-details request budget exhausted')
            now = time.monotonic()
            delay = max(self.next_request, self.cooldown_until) - now
            if delay > 0:
                return delay
            self.next_request = now + self.request_interval
            self.count_request(details)
            return 0

    def count_request(self, details):
        if details:
            self.detail_requests += 1
        else:
            self.export_requests += 1

    @staticmethod
    def get_retry_delay(value, attempt):
        if value is None:
            return 2 ** attempt
        try:
            return max(0, float(value))
        except ValueError:
            return max(0, parsedate_to_datetime(value).timestamp() - time.time())

    def download(self, url, label, details=False):
        request = Request(url, headers={'User-Agent': 'TMDbHelper-CollectionsBuilder'})
        for attempt in range(self.attempts):
            self.reserve_request(details)
            try:
                return self.get_response(request)
            except HTTPError as error:
                self.retry_http_error(error, label, attempt)
            except (URLError, TimeoutError, ConnectionError, HTTPException):
                self.retry_connection_error(label, attempt)
        raise CollectionAPIError(f'{label}: request failed')

    @staticmethod
    def get_response(request):
        with urlopen(request, timeout=30) as response:
            return response.read()

    def retry_http_error(self, error, label, attempt):
        status = error.code
        retry_after = error.headers.get('Retry-After')
        error.close()
        if status not in (429, 500, 502, 503, 504) or attempt == self.attempts - 1:
            raise CollectionAPIError(f'{label}: HTTP {status}', status) from None
        delay = self.get_retry_delay(retry_after, attempt)
        if status == 429:
            self.set_cooldown(delay)
        time.sleep(delay)

    def set_cooldown(self, delay):
        with self.lock:
            self.cooldown_until = max(self.cooldown_until, time.monotonic() + delay)

    def retry_connection_error(self, label, attempt):
        if attempt == self.attempts - 1:
            raise CollectionAPIError(f'{label}: connection failed') from None
        time.sleep(2 ** attempt)

    def get_export(self, snapshot_date):
        name = f'collection_ids_{snapshot_date:%m_%d_%Y}.json.gz'
        filename = self.cache_directory / name
        try:
            content = filename.read_bytes()
        except FileNotFoundError:
            return self.download_export(filename, snapshot_date)
        return self.get_export_data(content)

    def download_export(self, filename, snapshot_date):
        content = self.download(f'{self.export_url}/{filename.name}', f'Export {snapshot_date}')
        data = self.get_export_data(content)  # Validate before caching a complete snapshot.
        filename.parent.mkdir(parents=True, exist_ok=True)
        temporary = filename.with_suffix('.tmp')
        temporary.write_bytes(content)
        os.replace(temporary, filename)
        return data

    def get_export_data(self, content):
        identifiers = self.parse_export(content)
        return identifiers, hashlib.sha256(content).hexdigest(), len(content)

    @staticmethod
    def parse_export(content):
        records = [json.loads(line) for line in gzip.decompress(content).splitlines()]
        identifiers = [record['id'] for record in records]
        if not identifiers or any(type(value) is not int or value <= 0 for value in identifiers):
            raise ValueError('Invalid or empty collection-ID export')
        if len(set(identifiers)) != len(identifiers):
            raise ValueError('Duplicate collection IDs in export')
        return identifiers

    def get_collection(self, collection_id):
        query = urlencode({'api_key': self.api_key, 'language': 'en-US'})
        content = self.download(
            f'{self.api_url}/collection/{collection_id}?{query}',
            f'Collection {collection_id}', details=True)
        response = json.loads(content)
        return self.map_collection(response, collection_id)

    def map_collection(self, response, collection_id):
        if response['id'] != collection_id:
            raise ValueError(f'Collection {collection_id}: mismatched response ID')
        movies = [self.map_movie(item, collection_id) for item in response['parts']]
        return self.get_unique_movies(movies, collection_id)

    @staticmethod
    def map_movie(item, collection_id):
        movie_id = item['id']
        release = item.get('release_date') or None
        if type(movie_id) is not int or movie_id <= 0:
            raise ValueError(f'Collection {collection_id}: invalid movie ID')
        if release is not None:
            datetime.strptime(release, '%Y-%m-%d')
        return movie_id, release

    @staticmethod
    def get_unique_movies(movies, collection_id):
        # TMDb can repeat an identical part (for example collection 63170).
        # Collapse exact repeats, but do not choose between conflicting dates.
        unique_movies = list(dict.fromkeys(movies))
        if len({movie_id for movie_id, release in unique_movies}) != len(unique_movies):
            raise ValueError(f'Collection {collection_id}: conflicting release dates for a movie')
        return unique_movies


def get_utc_timestamp():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')
