from tmdbhelper.lib.addon.logger import kodi_traceback
from tmdbhelper.lib.files.scache import SimpleCache
from jurialmunkey.futils import get_filecache_name
from jurialmunkey.scache import TIME_HOURS
from jurialmunkey.tmdate import set_timestamp
import jurialmunkey.bcache

use_simple_cache = jurialmunkey.bcache.use_simple_cache


class BasicCache(jurialmunkey.bcache.BasicCache):
    _queue_limit = 250
    _simplecache = SimpleCache

    @staticmethod
    def kodi_traceback(exc, log_msg):
        kodi_traceback(exc, log_msg)

    def get_stale_cache(self, cache_name, stale_hours):
        """Return an entry that is current or expired less than stale_hours ago."""
        self.ret_cache()
        cache_name = get_filecache_name(cache_name or '')
        return self._cache.get(cache_name, cur_time=set_timestamp(-stale_hours * TIME_HOURS, True))


class BasicCacheService(BasicCache):
    _queue_limit = 20
