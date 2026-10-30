"""Small standard-library API clients for maintenance outside Kodi."""
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import time


class AwardsAPIError(RuntimeError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class JsonClient:
    headers = None
    query_defaults = None
    attempts = 5

    def request(self, path, params=None, payload=None):
        query = dict(self.query_defaults or {})
        query.update(params or {})
        url = f'{self.base_url}/{path}'
        url = f'{url}?{urlencode(query)}' if query else url
        headers = {'Accept': 'application/json', 'User-Agent': 'TMDbHelper-AwardsBuilder'}
        headers.update(self.headers or {})
        data = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload).encode('utf-8')
        request = Request(url, data=data, headers=headers)
        for attempt in range(self.attempts):
            try:
                with urlopen(request, timeout=60) as response:
                    return json.load(response)
            except HTTPError as error:
                status = error.code
                delay = error.headers.get('Retry-After')
                error.close()
                if status not in (429, 500, 502, 503, 504) or attempt == self.attempts - 1:
                    raise AwardsAPIError(f'{self.provider} {path}: HTTP {status}', status=status) from None
                time.sleep(self.get_retry_delay(delay, attempt))
            except (URLError, TimeoutError, ConnectionError, HTTPException):
                if attempt == self.attempts - 1:
                    raise AwardsAPIError(f'{self.provider} {path}: connection failed') from None
                time.sleep(2 ** attempt)
        raise AwardsAPIError(f'{self.provider} {path}: request failed')

    @staticmethod
    def get_retry_delay(value, attempt):
        if value is None:
            return 2 ** attempt
        try:
            return float(value)
        except ValueError:
            return max(0, parsedate_to_datetime(value).timestamp() - time.time())


class TVDbClient(JsonClient):
    provider = 'TVDB'
    base_url = 'https://api4.thetvdb.com/v4'

    def __init__(self, api_key):
        token = self.request('login', payload={'apikey': api_key})['data']['token']
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_data(self, path):
        response = self.request(path)
        if response['status'] != 'success':
            raise AwardsAPIError(f'TVDB {path}: unsuccessful response')
        return response['data']

    def get_item_details(self, tmdb_type, tvdb_id):
        path = f'{"movies" if tmdb_type == "movie" else "series"}/{tvdb_id}/extended'
        try:
            return self.get_data(path)
        except AwardsAPIError as error:
            if error.status != 404:
                raise
            return None


class TMDbClient(JsonClient):
    provider = 'TMDB'
    base_url = 'https://api.themoviedb.org/3'

    def __init__(self, api_key):
        self.query_defaults = {'api_key': api_key, 'language': 'en-US'}

    def get_tmdb_id(self, tmdb_type, tvdb_id, name, year):
        if tmdb_type == 'tv':
            response = self.request(f'find/{tvdb_id}', {'external_source': 'tvdb_id'})
            if response['tv_results']:
                return response['tv_results'][0]['id']
            if response.get('tv_episode_results'):
                return response['tv_episode_results'][0]['show_id']
        return self.search_id(tmdb_type, name, year)

    def search_id(self, tmdb_type, name, year):
        params = {'query': name}
        if year:
            params['year' if tmdb_type == 'movie' else 'first_air_date_year'] = year
        response = self.request(f'search/{tmdb_type}', params)
        return next(
            (item['id'] for item in response['results'] if self.matches(item, tmdb_type, name, year)),
            None)

    def get_item_details(self, tmdb_type, tmdb_id):
        try:
            return self.request(f'{tmdb_type}/{tmdb_id}')
        except AwardsAPIError as error:
            if error.status != 404:
                raise
            return None

    def find_ids(self, tmdb_type, external_id, source):
        response = self.request(f'find/{external_id}', {'external_source': source})
        identifiers = {item['id'] for item in response[f'{tmdb_type}_results']}
        if tmdb_type == 'tv':
            identifiers.update(item['show_id'] for item in response.get('tv_episode_results', []))
            identifiers.update(item['show_id'] for item in response.get('tv_season_results', []))
        return identifiers

    def search_items(self, tmdb_type, name, year=None):
        params = {'query': name, 'page': 1}
        if year:
            params['year' if tmdb_type == 'movie' else 'first_air_date_year'] = year
        while True:
            response = self.request(f'search/{tmdb_type}', params)
            yield from response['results']
            if params['page'] >= response['total_pages']:
                return
            params['page'] += 1

    @staticmethod
    def matches(item, tmdb_type, name, year):
        title_key, date_key = ('title', 'release_date') if tmdb_type == 'movie' else ('name', 'first_air_date')
        return (
            (item[title_key] or '').casefold() == name.casefold()
            and (not year or int((item[date_key] or '9999')[:4]) == int(year)))
