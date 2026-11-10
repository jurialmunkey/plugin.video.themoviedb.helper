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

    After a successful refresh, an item type is not checked again while its providers'
    last activities are unchanged: every change that needs a new sync replaces or clears
    them, and they expire so that the provider is asked again.
    """

    max_workers = 2  # One movie and one show refresh at a time

    def __init__(self):
        self.lock = RLock()
        self.refreshes = {}
        self.preparations = {}
        self.current_markers = {}  # Last activities seen after each item type's last successful refresh
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix='TMDbHelper sync')

    def get_preparation(self, item_type):
        # Selected providers only change with settings, which restart the service.
        try:
            return self.preparations[item_type]
        except KeyError:
            preparation = self.preparations[item_type] = SyncPreparation(item_type)
            return preparation

    def is_current(self, item_type):
        markers = self.get_preparation(item_type).activity_markers
        return None not in markers and self.current_markers.get(item_type) == markers

    def set_current(self, item_type):
        with self.lock:
            self.current_markers[item_type] = self.get_preparation(item_type).activity_markers

    def refresh(self, item_types):
        """Start refreshing the item types that are not current or already refreshing."""
        with self.lock:
            return [
                self.get_refresh(item_type)
                for item_type in item_types
                if not self.is_current(item_type)
            ]

    def get_refresh(self, item_type):
        try:
            return self.refreshes[item_type]
        except KeyError:
            pass
        future = self.refreshes[item_type] = self.executor.submit(self.sync, item_type)
        future.add_done_callback(lambda future, item_type=item_type: self.remove(item_type, future))
        return future

    def remove(self, item_type, future):
        # Later lists check again unless the last activities are unchanged since a successful refresh.
        with self.lock:
            if self.refreshes.get(item_type) is future:
                del self.refreshes[item_type]

    def sync(self, item_type):
        try:
            if SyncPreparation(item_type).sync():
                self.set_current(item_type)
        except Exception:
            kodi_log(f'Item detail sync refresh failed for {item_type}:\n{format_exc()}', 1)

    def wait(self, item_types, timeout):
        """Refresh the item types and wait for them, as lists waited before building items."""
        futures = self.refresh(item_types)
        if futures:
            wait(futures, timeout=timeout)

    def close(self):
        self.executor.shutdown(wait=False)
