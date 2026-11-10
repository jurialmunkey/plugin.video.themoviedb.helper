"""Bounded reuse of assembled item metadata on one database-owning thread."""

from collections import OrderedDict, deque
from copy import deepcopy
from itertools import chain
from sys import getsizeof
from jurialmunkey.ftools import cached_property


class MetadataSizeEstimator:
    """Estimate retained metadata containers, counting shared values once."""

    def __init__(self, value):
        self.value = value
        self.current_value = None
        self.seen = set()
        self.total_size = 0

    @cached_property
    def pending(self):
        return self.get_pending()

    def get_pending(self):
        return deque([self.value])

    @property
    def current_identity(self):
        return id(self.current_value)

    @property
    def current_size(self):
        return getsizeof(self.current_value)

    @property
    def children(self):
        return self.get_children()

    def get_children(self):
        if isinstance(self.current_value, dict):
            return chain.from_iterable(self.current_value.items())
        if isinstance(self.current_value, (list, tuple)):
            return self.current_value
        return ()

    @cached_property
    def size(self):
        return self.get_size()

    def get_size(self):
        while self.pending:
            self.process_next()
        return self.total_size

    def process_next(self):
        self.current_value = self.pending.pop()
        if self.current_identity in self.seen:
            return
        self.seen.add(self.current_identity)
        self.total_size += self.current_size
        self.pending.extend(self.children)


class SegmentedMetadataEntries:
    """Keep reused entries apart from entries seen once (segmented LRU).

    New entries start in the trial segment and move to the protected segment when found
    again, so items seen once, such as a browsed filmography, cannot push out reused items,
    such as widget items. Values are (item, size) pairs.
    """

    def __init__(self, protected_limit):
        self.protected_limit = protected_limit
        self.trial = OrderedDict()
        self.protected = OrderedDict()

    def __len__(self):
        return len(self.trial) + len(self.protected)

    def __iter__(self):
        return chain(self.trial, self.protected)

    def __contains__(self, key):
        return key in self.trial or key in self.protected

    def touch(self, key):
        """Return an entry's value, making it the newest protected entry."""
        if key in self.protected:
            self.protected.move_to_end(key)
            return self.protected[key]
        value = self.trial.pop(key)
        self.protected[key] = value
        self.demote_excess()
        return value

    def demote_excess(self):
        """Return the oldest protected entries to the trial segment rather than evicting them."""
        while len(self.protected) > self.protected_limit:
            key, value = self.protected.popitem(last=False)
            self.trial[key] = value

    def add(self, key, value, protected=False):
        if not protected:
            self.trial[key] = value
            return
        self.protected[key] = value
        self.demote_excess()

    def remove(self, key):
        """Remove an entry, returning its value and whether it was protected."""
        if key in self.protected:
            return self.protected.pop(key), True
        return self.trial.pop(key), False

    def pop(self, key):
        value, _ = self.remove(key)
        return value

    def pop_oldest(self):
        """Remove the oldest trial entry, or the oldest protected entry once trial is empty."""
        segment = self.trial or self.protected
        return segment.popitem(last=False)

    def clear(self):
        self.trial.clear()
        self.protected.clear()


class ItemMetadataCache:
    max_entries = 512
    max_bytes = 16 * 1024 * 1024
    protected_share = 0.8  # Share of entries kept for items found again

    def __init__(self, database):
        self.database = database
        self.connection = None
        self.version = None
        self.entries = SegmentedMetadataEntries(self.protected_entries)
        self.size = 0

    @property
    def protected_entries(self):
        return int(self.max_entries * self.protected_share)

    @property
    def is_full(self):
        return len(self.entries) >= self.max_entries

    def get_version(self):
        # data_version is comparable only on the same connection. Keep this
        # observer separate from the service's short-lived read/write cursors;
        # it also sees commits made by the service itself.
        if self.connection is None:
            self.connection = self.database.get_database(read_only=True)
        return self.connection.execute('PRAGMA data_version').fetchone()[0]

    def invalidate(self):
        self.entries.clear()
        self.size = 0

    def synchronise(self):
        version = self.get_version()
        if self.version is not None and version != self.version:
            self.invalidate()
        self.version = version
        return version

    @staticmethod
    def get_key(mapper):
        factory = mapper.parent_db_cache
        return (
            type(mapper),
            factory.item_id,
            factory.language,
            mapper.extendedinfo,
            factory.datalevel,
            factory.translation,
            tuple(tuple(row) for row in mapper.data),
        )

    def get_entry(self, key):
        try:
            item, _ = self.entries.touch(key)
        except KeyError:
            return
        return item

    @staticmethod
    def get_size(value):
        # Count shared values once within an entry. Counting them again across
        # entries conservatively bounds retained memory, including cache keys.
        return MetadataSizeEstimator(value).size

    def evict_oldest(self):
        _, (_, size) = self.entries.pop_oldest()
        self.size -= size

    def release_entry(self, key):
        """Remove an entry that is about to be replaced; return whether it was protected."""
        try:
            (_, size), is_protected = self.entries.remove(key)
        except KeyError:
            return False
        self.size -= size
        return is_protected

    def make_room(self, size):
        while self.entries and (
            self.is_full or self.size + size > self.max_bytes
        ):
            self.evict_oldest()

    def set_entry(self, key, item):
        size = self.get_size((key, item))
        if size > self.max_bytes:
            return False
        # Two readers can assemble the same item. Replace the one stored first in its
        # segment, and count only the replacement's size.
        is_protected = self.release_entry(key)
        self.make_room(size)
        self.entries.add(key, (item, size), protected=is_protected)
        self.size += size
        return True

    def copy_item(self, item):
        # Mappers and downstream consumers may mutate nested output containers.
        return deepcopy(item)

    def get_item(self, mapper):
        version = self.synchronise()
        key = self.get_key(mapper)
        item = self.get_entry(key)
        if item is not None:
            return self.copy_item(item)
        return self.get_uncached_item(mapper, key, version)

    def get_uncached_item(self, mapper, key, version):
        item = mapper.get_stable_item()
        # Retain the fragment only if its database revision is unchanged.
        if self.synchronise() != version:
            return item
        if not self.set_entry(key, item):
            return item
        return self.copy_item(item)

    def close(self):
        self.invalidate()
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.version = None
