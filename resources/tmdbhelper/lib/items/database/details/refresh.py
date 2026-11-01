from concurrent.futures import ThreadPoolExecutor, wait
from threading import RLock
from traceback import format_exc
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.sync.prepare import SyncPreparation


class DetailsSyncRefresher:
    """Refresh synced play data once for every list that needs it.

    A refresh already in progress for an item type is shared, so widgets loading
    together wait on one refresh instead of each checking for themselves. Refreshes
    run off the coordinator so that lists without synced data are not held up.
    """

    max_workers = 2  # One movie and one show refresh at a time

    def __init__(self):
        self.lock = RLock()
        self.refreshes = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix='TMDbHelper sync')

    def refresh(self, item_types):
        """Start refreshing the item types that are not already refreshing."""
        with self.lock:
            return [self.get_refresh(item_type) for item_type in item_types]

    def get_refresh(self, item_type):
        try:
            return self.refreshes[item_type]
        except KeyError:
            pass
        future = self.refreshes[item_type] = self.executor.submit(self.sync, item_type)
        future.add_done_callback(lambda future, item_type=item_type: self.remove(item_type, future))
        return future

    def remove(self, item_type, future):
        # Later lists check again: the check is quick while the data is fresh.
        with self.lock:
            if self.refreshes.get(item_type) is future:
                del self.refreshes[item_type]

    @staticmethod
    def sync(item_type):
        try:
            SyncPreparation(item_type).sync()
        except Exception:
            kodi_log(f'Item detail sync refresh failed for {item_type}:\n{format_exc()}', 1)

    def wait(self, item_types, timeout):
        """Refresh the item types and wait for them, as lists waited before building items."""
        futures = self.refresh(item_types)
        if futures:
            wait(futures, timeout=timeout)

    def close(self):
        self.executor.shutdown(wait=False)
