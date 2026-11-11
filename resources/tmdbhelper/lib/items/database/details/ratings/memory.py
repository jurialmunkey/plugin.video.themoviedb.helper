from collections import OrderedDict
from threading import Lock
from tmdbhelper.lib.addon.tmdate import set_timestamp


class DetailsRatingsMemory:
    """Ratings kept until they expire, so that repeat requests skip the database.
    Changing ratings providers restarts the service, which clears them."""

    capacity = 500

    def __init__(self):
        self.lock = Lock()
        self.items = OrderedDict()

    @property
    def current_time(self):
        return set_timestamp(0, set_int=True)

    def get(self, key):
        """The item's ratings, or None when they are not held or have expired."""
        with self.lock:
            try:
                expiry, ratings = self.items[key]
            except KeyError:
                return
            if expiry < self.current_time:
                del self.items[key]
                return
            self.items.move_to_end(key)
            return ratings

    def set(self, key, ratings, expiry):
        with self.lock:
            self.items[key] = (expiry, ratings)
            self.items.move_to_end(key)
            while len(self.items) > self.capacity:
                self.items.popitem(last=False)
