"""Detailed measurements used only by the opt-in item detail profiler."""

from collections import deque
from contextlib import contextmanager
from cProfile import Profile
from itertools import chain
from sys import getsizeof
from threading import local
from tmdbhelper.lib.items.database.details.backend import DetailsDatabase


class DetailsWorkProfiler:
    """Profile one backend operation on its owning thread, without global factory patches."""

    fresh_methods = (
        'get_infoproperties_progress', 'get_infoproperties_lastplayed',
        'get_infoproperties_ranks', 'get_infoproperties_aired_episodes',
        'get_infoproperties_episode_type', 'get_age',
    )

    def __init__(self):
        self.local = local()

    @property
    def record(self):
        return getattr(self.local, 'record', None)

    @contextmanager
    def scope(self, record):
        if self.record is not None:
            yield
            return  # A commit can call read(); collect its function calls only once.
        profiler = Profile()
        self.local.record = record
        profiler.enable()
        try:
            yield
        finally:
            profiler.disable()
            self.local.record = None
            with record.measure('profile_collect'):
                self.collect(record, profiler.getstats())

    @staticmethod
    def get_function_name(code):
        if isinstance(code, str):
            return code if any(name in code for name in ('sqlite3.', '_sqlite3.', 'xbmc')) else None
        filename = code.co_filename.replace('\\', '/')
        if '/tmdbhelper/lib/' in filename:
            filename = filename.rsplit('/tmdbhelper/lib/', 1)[1]
            if filename.startswith('items/database/details/profiling'):
                return
        elif '/jurialmunkey/' in filename:
            filename = 'jurialmunkey/' + filename.rsplit('/jurialmunkey/', 1)[1]
        else:
            return
        return f'{filename}:{code.co_firstlineno}:{code.co_name}'

    @classmethod
    def get_stage(cls, code):
        if isinstance(code, str):
            return
        filename = code.co_filename.replace('\\', '/')
        name = code.co_name
        if '/baseitem_factories/' in filename and name == 'get_item_meta':
            return 'item_mapping'
        if filename.endswith('/basemeta_factories/concrete_classes/sync.py') and name == 'get_cached_data':
            return 'synced_state_read'
        if '/itemmeta_factories/' in filename and name in cls.fresh_methods:
            return 'fresh_state_mapping'
        if filename.endswith('/items/database/mappings.py') and name == 'get_custom_date':
            return 'date_mapping'

    def collect(self, record, entries):
        functions = {}
        for entry in entries:
            name = self.get_function_name(entry.code)
            if name is not None:
                previous = functions.get(name, (0, 0, 0))
                values = (entry.callcount, entry.totaltime, entry.inlinetime)
                functions[name] = tuple(a + b for a, b in zip(previous, values))
            stage = self.get_stage(entry.code)
            if stage is not None:
                record.add_time(stage, entry.totaltime)
                record.count(f'{stage}_calls', entry.callcount)
        record.add_functions(functions)


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
