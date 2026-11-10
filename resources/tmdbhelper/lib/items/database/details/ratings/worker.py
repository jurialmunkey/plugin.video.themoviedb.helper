from concurrent.futures import CancelledError, Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from threading import RLock, local
from traceback import format_exc
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.items.database.details.apis import DetailsAPIs
from tmdbhelper.lib.items.database.details.protocol import DetailsLookupError
from tmdbhelper.lib.items.database.details.ratings.awards import DetailsRatingsAwards
from tmdbhelper.lib.items.database.details.ratings.lookup import DetailsRatingsItem, DetailsRatingsLookup
from tmdbhelper.lib.items.database.details.ratings.memory import DetailsRatingsMemory
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings


class DetailsRatingsWorker:
    """Ratings for the service monitor, the player monitor and lists.

    Monitors prewarm the ratings of the item they show with its details request, then
    ask for them separately so that the details are not held up. The monitor lane runs
    one lookup and keeps one waiting: a newer item replaces the waiting one, so lookups
    do not pile up while scrolling. Lists receive ratings with their items from a pooled
    lane that is never replaced. Every request for an item shares its lookup in progress.
    Ratings are returned first and saved afterwards.
    """

    list_workers = 8

    def __init__(self):
        self.lock = RLock()
        self.lookups = {}  # Lookup futures by item key while queued or running
        self.waiting = None  # The monitor lane's queued lookup, which a newer item replaces
        self.memory = DetailsRatingsMemory()
        self.apis = DetailsAPIs()
        self.local = local()
        self.monitor_lane = ThreadPoolExecutor(max_workers=1, thread_name_prefix='TMDbHelper ratings')
        self.list_lane = ThreadPoolExecutor(max_workers=self.list_workers, thread_name_prefix='TMDbHelper list ratings')
        self.saves = ThreadPoolExecutor(max_workers=1, thread_name_prefix='TMDbHelper ratings save')

    @cached_property
    def awards_database(self):
        return self.get_awards_database()

    @staticmethod
    def get_awards_database():
        from tmdbhelper.lib.awards.database import AwardsDatabase
        return AwardsDatabase()

    def get_ratings_settings(self):
        """One provider registry per lane thread: provider sessions are reused, not shared."""
        try:
            return self.local.ratings_settings
        except AttributeError:
            pass
        ratings_settings = self.local.ratings_settings = RatingsProviderSettings()
        return ratings_settings

    def prewarm(self, request):
        """Start the lookup for the item that a monitor will ask for next."""
        item = DetailsRatingsItem(request)
        if not item.is_rated or self.memory.get(item.key) is not None:
            return
        self.get_monitor_lookup(item)

    def get_monitor_ratings(self, request, awards=False, timeout=None):
        item = DetailsRatingsItem(request)
        if not item.is_rated:
            return {}
        ratings = self.memory.get(item.key)
        if ratings is None:
            ratings = self.get_result(self.get_monitor_lookup(item), timeout)
        if not awards:
            return ratings
        return {**ratings, **self.get_awards(item)}

    def start_list_ratings(self, request):
        """A future for the ratings of a list item, or None when the item has no ratings."""
        item = DetailsRatingsItem(request)
        if not item.is_rated:
            return
        ratings = self.memory.get(item.key)
        if ratings is None:
            return self.get_list_lookup(item)
        future = Future()
        future.set_result(ratings)
        return future

    def get_awards(self, item):
        return DetailsRatingsAwards(self.awards_database, item.tmdb_type, item.request.tmdb_id).info

    def get_monitor_lookup(self, item):
        with self.lock:
            try:
                return self.lookups[item.key]
            except KeyError:
                pass
            self.replace_waiting()
            future = self.waiting = self.submit(self.monitor_lane, item)
            return future

    def replace_waiting(self):
        """Drop the queued lookup of an item that monitors have moved on from.
        A lookup that has started cannot be cancelled and is left to finish."""
        if self.waiting is not None:
            self.waiting.cancel()

    def get_list_lookup(self, item):
        """Share a lookup unless it is the monitor lane's waiting one, which may be replaced."""
        with self.lock:
            future = self.lookups.get(item.key)
            if future is not None and (future is not self.waiting or future.running()):
                return future
            return self.submit(self.list_lane, item)

    def submit(self, lane, item):
        future = self.lookups[item.key] = lane.submit(self.lookup, item)
        future.add_done_callback(lambda future, key=item.key: self.remove(key, future))
        return future

    def remove(self, key, future):
        with self.lock:
            if self.lookups.get(key) is future:
                del self.lookups[key]

    def lookup(self, item):
        try:
            return self.get_lookup_ratings(item)
        except Exception:
            kodi_log(f'Item ratings lookup failed for {item.key}:\n{format_exc()}', 1)
            raise

    def get_lookup_ratings(self, item):
        lookup = DetailsRatingsLookup(item, self.apis.get(item.request.language), self.get_ratings_settings())
        ratings = lookup.ratings
        if ratings:  # Empty ratings are retried next time, as an empty saved row is
            self.memory.set(item.key, ratings, lookup.expiry)
        if lookup.unsaved_levels:
            self.saves.submit(self.save, lookup)
        return ratings

    @staticmethod
    def save(lookup):
        try:
            lookup.save()
        except Exception:
            kodi_log(f'Item ratings were not saved for {lookup.item.key}:\n{format_exc()}', 1)

    @staticmethod
    def get_result(future, timeout):
        """The lookup's ratings. A replaced lookup has none, as its item is no longer shown."""
        try:
            return future.result(timeout=timeout)
        except CancelledError:
            return {}
        except FutureTimeoutError:
            raise DetailsLookupError('Item ratings lookup timed out')
        except Exception as exc:
            raise DetailsLookupError(f'Item ratings lookup failed: {exc}')

    def close(self):
        with self.lock:
            self.replace_waiting()
        self.monitor_lane.shutdown(wait=False)
        self.list_lane.shutdown(wait=False)
        self.saves.shutdown(wait=False)
