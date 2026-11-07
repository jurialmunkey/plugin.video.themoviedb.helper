"""Detailed measurements used only by the opt-in item detail profiler."""

from collections import deque
from itertools import chain
from sys import getsizeof
from threading import local
from tmdbhelper.lib.items.database.details.backend import DetailsDatabase
from tmdbhelper.lib.items.database.details.metadata import DetailsMetadataCache


class DetailsWorkProfiler:
    """Attach explicit database/factory/mapper timers to the owning thread's item."""

    def __init__(self):
        self.local = local()

    @property
    def record(self):
        return getattr(self.local, 'record', None)

    def call(self, record, func, *args):
        if self.record is not None:
            # A commit can call read(); both use the same item's timing record.
            return func(*args)
        self.local.record = record
        try:
            return func(*args)
        finally:
            self.local.record = None

    def call_stage(self, stage, func, *args):
        record = self.record
        if record is None:
            return func(*args)
        record.count(f'{stage}_calls')
        return record.call(stage, func, *args)


class ProfiledItemMetadataCache(DetailsMetadataCache):
    def __init__(self, database, profiler):
        super().__init__(database)
        self.profiler = profiler

    def get_entry(self, key):
        record = self.profiler.record
        if record is None:
            return super().get_entry(key)
        item = record.call('metadata_lookup', super().get_entry, key)
        record.count('metadata_hits' if item is not None else 'metadata_misses')
        return item

    def set_entry(self, key, item):
        record = self.profiler.record
        if record is None:
            return super().set_entry(key, item)
        before = len(self.entries)
        stored = record.call('metadata_store', super().set_entry, key, item)
        record.count('metadata_stores' if stored else 'metadata_oversized')
        record.count('metadata_evictions', before + int(stored) - len(self.entries))
        return stored

    def invalidate(self):
        record = self.profiler.record
        if record is not None:
            record.count('metadata_invalidations')
            record.count('metadata_invalidated_entries', len(self.entries))
        super().invalidate()

    def copy_item(self, item):
        record = self.profiler.record
        if record is None:
            return super().copy_item(item)
        return record.call('metadata_copy', super().copy_item, item)

    def discard_saved(self, factory):
        record = self.profiler.record
        if record is None:
            return super().discard_saved(factory)
        record.count(f'metadata_save_scope_{factory.metadata_save_scope}')
        return record.call('metadata_discard', super().discard_saved, factory)

    def discard_entry(self, key):
        record = self.profiler.record
        if record is not None:
            record.count('metadata_discarded_entries')
        super().discard_entry(key)


class ProfiledDetailsDatabase(DetailsDatabase):
    def __init__(self, profiler):
        self.profiler = profiler
        super().__init__()

    def database_execute(self, connection, query, data=None):
        record = self.profiler.record
        if record is None:
            return super().database_execute(connection, query, data)
        record.count('sql_execute_calls')
        operation = query.lstrip().split(None, 1)[0].lower()
        record.count(f'sql_{operation}_calls')
        if isinstance(data, list) and data:
            record.count('sql_executemany_calls')
            record.count('sql_parameter_sets', len(data))
        else:
            record.count('sql_parameter_sets')
        try:
            return record.call('sql_execute', super().database_execute, connection, query, data)
        except Exception:
            record.count('sql_errors')
            raise

    def get_list_values(self, table='simplecache', keys=(), values=(), conditions=None, connection=None):
        return self.read_rows(
            table, False, super().get_list_values, table, keys, values, conditions, connection)

    def get_values(self, table='simplecache', item_id=None, keys=(), connection=None):
        return self.read_rows(table, True, super().get_values, table, item_id, keys, connection)

    def read_rows(self, table, single_row, func, *args):
        record = self.profiler.record
        if record is None:
            return func(*args)
        table_name = table.split()[0]
        record.count('db_read_calls')
        record.count(f'db_read.{table_name}.calls')
        with record.measure('db_read'):
            if table_name == 'simplecache':
                rows = self.profiler.call_stage(
                    'synced_state_read', record.call, f'db_read.{table_name}', func, *args)
            else:
                rows = record.call(f'db_read.{table_name}', func, *args)
        row_count = (1 if single_row else len(rows)) if rows is not None else 0
        record.count('db_rows', row_count)
        record.count(f'db_read.{table_name}.rows', row_count)
        return rows


class DetailsMemoryEstimate:
    """Estimate unique Python containers and values; excludes native allocations and process RSS."""

    @staticmethod
    def get_size(value):
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
            elif isinstance(value, (list, tuple, set, frozenset, deque)):
                pending.extend(value)
        return size
