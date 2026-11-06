"""Share assembled item metadata between the item detail service's reader threads."""

from threading import RLock
from tmdbhelper.lib.items.database.baseitem_factories.metadata import ItemMetadataCache


class DetailsMetadataCache(ItemMetadataCache):
    """Guard shared entries and the version observer; assemble items outside the lock."""

    def __init__(self, database):
        super().__init__(database)
        self.lock = RLock()

    def get_version(self):
        # Readers take turns on one observer, so data_version stays comparable.
        if self.connection is None:
            self.connection = self.database.get_shared_database(read_only=True)
        return super().get_version()

    def synchronise(self):
        with self.lock:
            return super().synchronise()

    def invalidate(self):
        with self.lock:
            super().invalidate()

    def get_entry(self, key):
        with self.lock:
            return super().get_entry(key)

    def set_entry(self, key, item):
        with self.lock:
            return super().set_entry(key, item)

    def get_uncached_item(self, mapper, key, version):
        item = mapper.get_stable_item()
        # Check and store together so that another reader cannot invalidate in between.
        with self.lock:
            if self.synchronise() != version or not self.set_entry(key, item):
                return item
        return self.copy_item(item)

    def close(self):
        with self.lock:
            super().close()
