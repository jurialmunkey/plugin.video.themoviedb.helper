"""Share assembled item metadata between the item detail service's reader threads."""

from threading import RLock
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseitem_factories.metadata import ItemMetadataCache


class DetailsSavedItemScope:
    """Select the cached entries that a family-scoped save can change.

    Entry keys follow ItemMetadataCache.get_key(): the mapper class, then the item id.
    """

    def __init__(self, item_id, keys):
        self.item_id = item_id
        self.keys = keys

    @cached_property
    def family_id(self):
        return self.get_family_id()

    def get_family_id(self):
        # Seasons and episodes extend their show's id, e.g. tv.123.1.5 belongs to tv.123.
        return '.'.join(self.item_id.split('.')[:2])

    def is_family(self, item_id):
        return item_id == self.family_id or item_id.startswith(f'{self.family_id}.')

    @cached_property
    def discarded_keys(self):
        return self.get_discarded_keys()

    def get_discarded_keys(self):
        return [
            key
            for key in self.keys
            if key[0].reads_other_items or self.is_family(key[1])
        ]


class DetailsMetadataCache(ItemMetadataCache):
    """Guard shared entries; assemble items outside the lock.

    Item details are only saved by this service, so entries are not checked against
    database-wide changes: writes to ratings and synced play data do not affect them.
    Service saves discard the entries they can change through discard_saved().
    Code outside the service that changes cached details, including user artwork,
    must call DetailsClient().invalidate().

    Entries missing from memory are read from stored_metadata (a DetailsStoredMetadata)
    before they are assembled, and newly assembled entries are queued for storage.
    """

    # Hold every home screen widget's items alongside items browsed in dialogs and lists.
    # Entries average about 15 KB, so the byte limit is usually reached first.
    max_entries = 2048
    max_bytes = 32 * 1024 * 1024

    def __init__(self, database, stored_metadata):
        super().__init__(database)
        self.stored_metadata = stored_metadata
        self.lock = RLock()
        self.revision = 0

    def synchronise(self):
        """Return the revision; clearing advances it so items built meanwhile are not stored."""
        with self.lock:
            return self.revision

    def invalidate(self):
        with self.lock:
            super().invalidate()
            self.stored_metadata.discard_all()
            self.revision += 1

    def get_entry(self, key):
        with self.lock:
            return super().get_entry(key)

    def set_entry(self, key, item):
        with self.lock:
            return super().set_entry(key, item)

    def get_stored_item(self, mapper, key):
        """Read a stored copy on the reading thread's own connection."""
        return self.stored_metadata.read(key, mapper.parent_db_cache.connection.open_connection)

    def get_assembled_item(self, mapper, key):
        """Assemble an item and prepare its stored copy outside the lock."""
        from tmdbhelper.lib.items.database.details.storedmetadata import DetailsStoredMetadataCopy
        stored = DetailsStoredMetadataCopy(key, mapper.get_stable_item())
        stored.hash, stored.text  # Hash and encode before taking the lock
        return stored

    def get_new_item(self, mapper, key):
        """Return the item and, when it was assembled rather than read, its stored copy."""
        item = self.get_stored_item(mapper, key)
        if item is not None:
            return item, None
        stored = self.get_assembled_item(mapper, key)
        return stored.item, stored

    def queue_stored_copy(self, stored):
        self.stored_metadata.queue(stored)

    def get_uncached_item(self, mapper, key, version):
        item, stored = self.get_new_item(mapper, key)
        # Check and store together so that another reader cannot invalidate in between.
        with self.lock:
            if self.synchronise() != version:
                return item
            if stored is not None:
                self.queue_stored_copy(stored)
            if not self.set_entry(key, item):
                return item
        return self.copy_item(item)

    def discard_saved(self, factory):
        """Discard entries that the service's save of this factory's item can change."""
        with self.lock:
            if factory.metadata_save_scope != 'family':
                self.invalidate()
                return
            self.stored_metadata.discard_saved(factory)
            scope = DetailsSavedItemScope(factory.item_id, tuple(self.entries))
            for key in scope.discarded_keys:
                self.discard_entry(key)

    def discard_entry(self, key):
        _, size = self.entries.pop(key)
        self.size -= size

    def close(self):
        with self.lock:
            super().close()
