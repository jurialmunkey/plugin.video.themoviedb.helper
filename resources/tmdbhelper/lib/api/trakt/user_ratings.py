from hashlib import sha256
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.consts import TRAKT_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.files.bcache import BasicCache


class TraktUserRating:
    def __init__(self, trakt_api, item_type, trakt_id):
        self.trakt_api = trakt_api
        self.item_type = item_type
        self.trakt_id = trakt_id

    @cached_property
    def rating(self):
        return self.get_rating()

    def get_rating(self):
        return TraktUserRatings(self.trakt_api, self.item_type).ratings.get(str(self.trakt_id))


class TraktUserRatings:
    cache_days = 1 / 72  # Maximum snapshot lifetime; activity is checked on every lookup.
    item_types = ('movie', 'show', 'season', 'episode')

    def __init__(self, trakt_api, item_type):
        self.trakt_api = trakt_api
        self.item_type = item_type

    @cached_property
    def cache(self):
        return self.get_cache()

    def get_cache(self):
        return BasicCache()

    @cached_property
    def cache_name(self):
        return self.get_cache_name()

    def get_cache_name(self):
        account = sha256((self.trakt_api.access_token or '').encode('utf-8')).hexdigest()
        return f'TraktUserRatings.{account}.{self.item_type}'

    @cached_property
    def ratings(self):
        return self.get_ratings()

    @cached_property
    def last_activity(self):
        return self.get_last_activity()

    def get_last_activity(self):
        response = self.trakt_api.get_response('sync', 'last_activities')
        if response is None or response.status_code != 200:
            return
        try:
            data = response.json()
        except ValueError:
            return
        return data.get(f'{self.item_type}s', {}).get('rated_at') or None

    def get_ratings(self):
        cached = self.cache.get_cache(self.cache_name)
        last_activity = self.last_activity
        if cached is not None and last_activity is not None and cached.get('rated_at') == last_activity:
            return cached['ratings']
        ratings = self.get_response_ratings()
        if ratings is None:
            return {}
        if last_activity is not None:
            data = {'ratings': ratings, 'rated_at': last_activity}
            self.cache.set_cache(data, self.cache_name, cache_days=self.cache_days)
        return ratings

    def invalidate(self):
        self.cache.del_cache(self.cache_name)

    def get_response_ratings(self):
        ratings = {}
        page = 1
        while True:
            response = self.trakt_api.get_response(
                'sync', 'ratings', f'{self.item_type}s', page=page, limit=TRAKT_MAX_ITEMS_PER_PAGE)
            if response is None or response.status_code != 200:
                return
            try:
                data = response.json()
            except ValueError:
                return
            ratings.update((str(item[self.item_type]['ids']['trakt']), item['rating']) for item in data)
            if page >= try_int(response.headers.get('x-pagination-page-count'), fallback=1):
                return ratings
            page += 1
