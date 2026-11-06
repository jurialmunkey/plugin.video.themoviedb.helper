"""Bounded reuse of assembled item metadata on one database-owning thread."""

from collections import OrderedDict, deque
from copy import deepcopy
from itertools import chain
from sys import getsizeof


class ItemMetadataCache:
    max_entries = 512
    max_bytes = 16 * 1024 * 1024

    def __init__(self, database):
        self.database = database
        self.connection = None
        self.version = None
        self.entries = OrderedDict()
        self.size = 0

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
            type(mapper), factory.item_id, factory.language, mapper.extendedinfo,
            factory.datalevel, factory.translation,
            tuple(tuple(row) for row in mapper.data),
        )

    def get_entry(self, key):
        try:
            entry = self.entries.pop(key)
        except KeyError:
            return
        self.entries[key] = entry
        return entry[0]

    @staticmethod
    def get_size(value):
        # Count shared values once within an entry. Counting them again across
        # entries conservatively bounds retained memory, including cache keys.
        seen = set()
        pending = deque([value])
        size = 0
        while pending:
            value = pending.pop()
            identity = id(value)
            if identity in seen:
                continue
            seen.add(identity)
            size += getsizeof(value)
            if isinstance(value, dict):
                pending.extend(chain.from_iterable(value.items()))
            elif isinstance(value, (list, tuple)):
                pending.extend(value)
        return size

    def set_entry(self, key, item):
        size = self.get_size((key, item))
        if size > self.max_bytes:
            return False
        while self.entries and (
                len(self.entries) >= self.max_entries or self.size + size > self.max_bytes):
            _, (_, old_size) = self.entries.popitem(last=False)
            self.size -= old_size
        self.entries[key] = (item, size)
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
        item = mapper.get_stable_item()
        # Never retain a fragment assembled across a concurrent database update.
        if self.synchronise() != version or not self.set_entry(key, item):
            return item
        return self.copy_item(item)

    def close(self):
        self.invalidate()
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.version = None
