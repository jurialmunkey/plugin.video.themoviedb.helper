#!/usr/bin/python
# -*- coding: utf-8 -*-
import jurialmunkey.scache
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.futils import FileUtils
import sqlite3


DEFAULT_TABLE = 'simplecache'


class DataBase:

    simplecache_columns = {
        'data': {'data': 'TEXT', 'sync': None}
    }
    lactivities_columns = {
        'data': {'data': 'TEXT', 'sync': None}
    }

    _database = None
    _basefolder = get_setting('cache_location', 'str') or ''
    _fileutils = FileUtils()  # Import to use plugin addon_data folder not the module one
    _db_timeout = 3.0
    _db_read_timeout = 1.0

    def __init__(self, folder=None, filename=None):
        '''Initialize our caching class'''
        folder = folder or jurialmunkey.scache.DATABASE_NAME
        basefolder = f'{self._basefolder}{folder}'
        filename = filename or 'defaultcache.db'

        self._db_file = self._fileutils.get_file_path(basefolder, filename, join_addon_data=basefolder == folder)
        self._sc_name = f'{folder}_{filename}_databaserowfactory'
        self.check_database_initialization()
        self.kodi_log(f"CACHE: Initialized: {self._sc_name} - Thread Safety Level: {sqlite3.threadsafety} - SQLite v{sqlite3.sqlite_version}")

    @property
    def window_home(self):
        from xbmcgui import Window
        return Window(10000)

    def get_window_property(self, name):
        return self.window_home.getProperty(name)

    def set_window_property(self, name, value):
        return self.window_home.setProperty(name, value)

    def del_window_property(self, name):
        return self.window_home.clearProperty(name)

    @property
    def database_init_property(self):
        return f'{self._sc_name}.database.init'

    @property
    def database_initialized(self):
        return self.get_window_property(self.database_init_property)

    def set_database_init(self):
        self.set_window_property(self.database_init_property, 'True')

    def del_database_init(self):
        self.del_window_property(self.database_init_property)

    @staticmethod
    def kodi_log(msg, level=0):
        kodi_log(msg, level)

    def check_database_initialization(self):
        if not self.database_initialized:
            self.init_database()
            return

    def _set_pragmas(self, connection):
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def init_database(self):
        import xbmcvfs
        from jurialmunkey.locker import MutexPropLock
        with MutexPropLock(f'{self._db_file}.lockfile', kodi_log=self.kodi_log):
            if xbmcvfs.exists(self._db_file):
                return
            database = self._create_database()
            self.set_database_init()
        return database

    def _create_database(self):
        try:
            self.kodi_log(f'CACHE: Initialising: {self._db_file}...', 1)
            connection = sqlite3.connect(self._db_file, timeout=5.0, isolation_level=None)
            connection = self._set_pragmas(connection)
            self.create_database_execute(connection)
            return connection
        except Exception as error:
            self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name}', 1)

    def _get_database(self, read_only=False, log_level=1):
        timeout = self._db_read_timeout if read_only else self._db_timeout
        try:
            connection = sqlite3.connect(self._db_file, timeout=timeout, isolation_level=None)
        except Exception as error:
            self.kodi_log(f'CACHE: ERROR while retrieving _database: {error}\n{self._sc_name}', log_level)
            return
        connection.row_factory = sqlite3.Row
        return self._set_pragmas(connection)

    def _execute_sql(self, query, data=None, read_only=False):
        '''little wrapper around execute and executemany to just retry a db command if db is locked'''

        def database_execute(database):
            try:
                if not data:
                    return database.execute(query)
                if isinstance(data, list):
                    return database.executemany(query, data)
                return database.execute(query, data)
            except sqlite3.OperationalError as operational_exception:
                self.kodi_log(f'CACHE: database OPERATIONAL ERROR! -- {operational_exception}\n{self._sc_name} -- read_only: {read_only}\n--query--\n{query}\n--data--\n{data}', 2)
            except Exception as other_exception:
                self.kodi_log(f'CACHE: database OTHER ERROR! -- {other_exception}\n{self._sc_name} -- read_only: {read_only}\n--query--\n{query}\n--data--\n{data}', 2)

        # always use new db object because we need to be sure that data is available for other simplecache instances
        try:
            with self._get_database(read_only=read_only) as database:
                return database_execute(database)

        except Exception as database_exception:
            self.kodi_log(f'CACHE: database GET DATABASE ERROR! -- {database_exception}\n{self._sc_name} -- read_only: {read_only}', 2)

    def set_activity(self, item_type, method, value):
        idx = f'{item_type}.{method}'
        query = 'INSERT OR REPLACE INTO lactivities( id, data) VALUES (?, ?)'
        return self._execute_sql(query, (idx, value, ))

    def get_activity(self, item_type, method):
        idx = f'{item_type}.{method}'
        query = 'SELECT data FROM lactivities WHERE id=? LIMIT 1'
        cache = self._execute_sql(query, (idx, ))
        if not cache:
            return
        cache = cache.fetchone()
        if not cache:
            return
        return cache[0]

    def set_list_values(self, values, keys, table=DEFAULT_TABLE):
        query = 'INSERT OR IGNORE INTO {table} ({keys}) VALUES ({values})'.format(
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]),
            table=table,
        )
        return self._execute_sql(query, values)

    def get_list_values(self, conditions, values, keys, table=DEFAULT_TABLE):
        query = 'SELECT {keys} FROM {table} WHERE {conditions}'.format(
            keys=', '.join(keys),
            table=table,
            conditions=conditions,
        )
        cache = self._execute_sql(query, values, read_only=True)
        if not cache:
            return
        return cache.fetchall()

    def get_values(self, idx, keys, table=DEFAULT_TABLE):
        query = 'SELECT {keys} FROM {table} WHERE id=? LIMIT 1'.format(
            keys=', '.join(keys),
            table=table)
        cache = self._execute_sql(query, (idx, ), read_only=True)
        if not cache:
            return
        return cache.fetchone()

    def set_values(self, idx, key_value_pairs, table=DEFAULT_TABLE):
        keys, values = zip(*key_value_pairs)
        query = 'UPDATE {table} SET {keys} WHERE id=?'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]),
            table=table)
        self.create_item(idx, table)
        return self._execute_sql(query, (*values, idx, ))

    def set_many_values(self, keys, data, table=DEFAULT_TABLE):
        """ {idx: key_value_pairs} """
        query = 'UPDATE {table} SET {keys} WHERE id=?'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]),
            table=table)
        self.create_many_items([idx for idx in data.keys()], table)
        return self._execute_sql(query, [(*values, idx, ) for idx, values in data.items()])

    def del_column_values(self, keys, item_type, table=DEFAULT_TABLE):
        query = 'UPDATE {table} SET {keys} WHERE item_type=?'.format(
            keys=', '.join([f'{k}=NULL' for k in keys]),
            table=table)
        return self._execute_sql(query, (item_type, ))

    def create_item(self, idx, table=DEFAULT_TABLE):
        query = 'INSERT OR IGNORE INTO {table}( id) VALUES (?)'.format(table=table)
        self._execute_sql(query, (idx,))

    def create_many_items(self, items, table=DEFAULT_TABLE):
        query = 'INSERT OR IGNORE INTO {table}( id) VALUES (?)'.format(table=table)
        self._execute_sql(query, [(idx,) for idx in items])

    @property
    def database_tables(self):
        return {
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
        }

    def create_database_execute(self, connection):
        for table, columns in self.database_tables.items():
            query = 'CREATE TABLE IF NOT EXISTS {}(id TEXT UNIQUE, {})'
            query = query.format(table, ', '.join([f'{k} {v["data"]}' for k, v in columns.items()]))
            connection.execute(query)

        connection.execute("CREATE INDEX idx ON simplecache(id)")


class DataBaseCache:
    def get_cached(self, item_id, key, table):
        data = self.cache.get_values(item_id, keys=(key, ), table=table)
        return data[0] if data else None

    def set_cached(self, item_id, key, table, data):
        if not data:
            return
        key_value_pair = (key, data,)
        self.cache.set_values(item_id, key_value_pairs=(key_value_pair, ), table=table)
        return data

    def use_cached(self, item_id, key, table, func, *args, **kwargs):
        data = self.get_cached(item_id, key, table)
        if not data:
            data = self.set_cached(item_id, key, table, func(*args, **kwargs))
        return data

    def set_cached_many(self, keys, table, data):
        if not data:
            return
        self.cache.set_many_values(keys=keys, data=data, table=table)
        return data

    def use_cached_many(self, conditions, values, keys, table, func, *args, **kwargs):
        data = self.cache.get_list_values(conditions, values, keys, table)
        if not data:
            data = self.set_cached_many(keys, table, func(*args, **kwargs))
            data = self.cache.get_list_values(conditions, values, keys, table) if data else None
        return data
