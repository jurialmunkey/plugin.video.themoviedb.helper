"""Download widget lists that were shown from an expired cache entry."""

from xbmc import Monitor
from jurialmunkey.ftools import cached_property
from jurialmunkey.futils import get_filecache_name
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.tmdate import get_timestamp, set_timestamp


class StaleListRefresh:
    """Save a new copy of a list after its expired copy was returned to Kodi.

    The widget shows the new list the next time Kodi loads it. Widgets showing the same
    list share one refresh; a claim left by a call that stopped part way lapses.
    """

    claim_seconds = 300

    def __init__(self, cache, cache_name, cache_days, function, instance, args, kwargs):
        self.cache = cache
        self.cache_name = cache_name
        self.cache_days = cache_days
        self.function = function
        self.instance = instance
        self.args = args
        self.kwargs = kwargs

    @cached_property
    def claim_name(self):
        return f'ListRefresh.{get_filecache_name(self.cache_name)}'

    @property
    def is_claimed(self):
        return bool(get_timestamp(get_property(self.claim_name, is_type=int)))

    def claim(self):
        get_property(self.claim_name, set_property=set_timestamp(self.claim_seconds, True))

    def release(self):
        get_property(self.claim_name, clear_property=True)

    @cached_property
    def items(self):
        return self.function(self.instance, *self.args, **self.kwargs)

    def run(self):
        if self.is_claimed:
            return
        self.claim()
        try:
            self.save_items()
        finally:
            self.release()

    def save_items(self):
        # Keep the expired copy when the download fails or Kodi is closing.
        if not self.items or Monitor().abortRequested():
            return
        self.cache.set_cache(self.items, self.cache_name, cache_days=self.cache_days)
        kodi_log(f'Refreshed expired widget list {self.cache_name}', 1)
