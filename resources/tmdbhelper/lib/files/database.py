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
    _db_timeout = 60.0
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

    def set_pragmas(self, connection):
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
            database = self.create_database()
            self.set_database_init()
        return database

    def create_database(self):
        try:
            self.kodi_log(f'CACHE: Initialising: {self._db_file}...', 1)
            connection = sqlite3.connect(self._db_file, timeout=self._db_timeout, isolation_level=None)
            connection = self.set_pragmas(connection)
            self.create_database_execute(connection)
            return connection
        except Exception as error:
            self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name}', 1)

    def get_database(self, read_only=False, log_level=1):
        timeout = self._db_read_timeout if read_only else self._db_timeout
        try:
            connection = sqlite3.connect(self._db_file, timeout=timeout, isolation_level=None)
        except Exception as error:
            self.kodi_log(f'CACHE: ERROR while retrieving _database: {error}\n{self._sc_name}', log_level)
            return
        connection.row_factory = sqlite3.Row
        return self.set_pragmas(connection)

    def database_execute(self, connection, query, data=None):
        try:
            if not data:
                return connection.execute(query)
            if isinstance(data, list):
                return connection.executemany(query, data)
            return connection.execute(query, data)
        except sqlite3.OperationalError as operational_exception:
            self.kodi_log(f'CACHE: database OPERATIONAL ERROR! -- {operational_exception}\n{self._sc_name}\n--query--\n{query}\n--data--\n{data}', 2)
        except Exception as other_exception:
            self.kodi_log(f'CACHE: database OTHER ERROR! -- {other_exception}\n{self._sc_name}\n--query--\n{query}\n--data--\n{data}', 2)

    def execute_sql(self, query, data=None, read_only=False, connection=None):
        '''little wrapper around execute and executemany to just retry a db command if db is locked'''
        # always use new db object because we need to be sure that data is available for other simplecache instances
        try:
            if connection:
                return self.database_execute(connection, query, data=data)
            with self.get_database(read_only=read_only) as connection:
                return self.database_execute(connection, query, data=data)
        except Exception as database_exception:
            self.kodi_log(f'CACHE: database GET DATABASE ERROR! -- {database_exception}\n{self._sc_name} -- read_only: {read_only}', 2)

    @staticmethod
    def statement_insert_or_ignore(table, keys=('id', )):
        return 'INSERT OR IGNORE INTO {table}({keys}) VALUES ({values})'.format(
            table=table,
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]))

    @staticmethod
    def statement_insert_or_replace(table, keys=('id', )):
        return 'INSERT OR REPLACE INTO {table}({keys}) VALUES ({values})'.format(
            table=table,
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]))

    @staticmethod
    def statement_delete_keys(table, keys, conditions='item_type=?'):
        return 'UPDATE {table} SET {keys} WHERE {conditions}'.format(
            table=table,
            keys=', '.join([f'{k}=NULL' for k in keys]),
            conditions=conditions)

    @staticmethod
    def statement_update_if_null(table, keys, conditions='id=?'):
        return 'UPDATE {table} SET {keys} WHERE {conditions}'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]), table=table, conditions=conditions)

    @staticmethod
    def statement_select_limit(table, keys, conditions='id=?'):
        return 'SELECT {keys} FROM {table} WHERE {conditions} LIMIT 1'.format(
            keys=', '.join(keys), table=table, conditions=conditions)

    @staticmethod
    def statement_select(table, keys, conditions):
        return 'SELECT {keys} FROM {table} WHERE {conditions}'.format(
            keys=', '.join(keys), table=table, conditions=conditions)

    def set_activity(self, item_type, method, value):
        return self.execute_sql(
            self.statement_insert_or_replace('lactivities', keys=('id', 'data')),
            (f'{item_type}.{method}', value, ))

    def get_activity(self, item_type, method):
        result = self.execute_sql(self.statement_select_limit('lactivities', keys=('data', )), (f'{item_type}.{method}', ))
        if not result:
            return
        result = result.fetchone()
        if not result:
            return
        return result[0]

    def set_list_values(self, table=DEFAULT_TABLE, keys=(), values=(), connection=None):
        if not values:
            return
        return self.execute_sql(self.statement_insert_or_ignore(table, keys), values, connection=connection)

    def get_list_values(self, table=DEFAULT_TABLE, keys=(), values=(), conditions=None, connection=None):
        result = self.execute_sql(
            self.statement_select(table, keys, conditions),
            data=values,
            read_only=True,
            connection=connection)
        if not result:
            return
        return result.fetchall()

    def get_values(self, table=DEFAULT_TABLE, item_id=None, keys=(), connection=None):
        result = self.execute_sql(
            self.statement_select_limit(table, keys),
            data=(item_id, ),
            read_only=True,
            connection=connection)

        if not result:
            return

        return result.fetchone()

    def set_item_values(self, table=DEFAULT_TABLE, item_id=None, keys=(), values=(), connection=None):
        """ Create a new row at id=item_id (or update if it exists) and then update null values with new data """
        self.create_item(
            table=table,
            item_id=item_id,
            connection=connection)

        return self.execute_sql(
            self.statement_update_if_null(table, keys),
            data=(*values, item_id, ),
            connection=connection)

    def set_many_values(self, table=DEFAULT_TABLE, keys=(), data=None, connection=None):
        """ data={item_id: ((key, value), (key, value))} """

        # Create new rows if items dont exist
        self.create_many_items(
            table=table,
            item_ids=[item_id for item_id in data.keys()],
            connection=connection)

        return self.execute_sql(
            self.statement_update_if_null(table, keys),
            data=[(*values, item_id, ) for item_id, values in data.items()],
            connection=connection)

    def del_column_values(self, table=DEFAULT_TABLE, keys=(), item_type=None, connection=None):
        return self.execute_sql(
            self.statement_delete_keys(table, keys),
            data=(item_type, ),
            connection=connection
        )

    def create_item(self, table=DEFAULT_TABLE, item_id=None, connection=None):
        self.execute_sql(
            self.statement_insert_or_ignore(table),
            data=(item_id,),
            connection=connection)

    def create_many_items(self, table=DEFAULT_TABLE, item_ids=(), connection=None):
        self.execute_sql(
            self.statement_insert_or_ignore(table),
            data=[(item_id,) for item_id in item_ids],
            connection=connection)

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

    connection = None

    # ======================================
    # Single item with single key/value pair
    # ======================================

    def get_cached(self, table, item_id, key):
        data = self.cache.get_values(table, item_id, keys=(key, ), connection=self.connection)
        return data[0] if data else None

    def set_cached(self, table, item_id, key, value):
        """ Set key to value for id=item_id in table """
        if not value:
            return
        self.cache.set_item_values(table, item_id, keys=(key, ), values=(value, ), connection=self.connection)
        return value

    def use_cached(self, table, item_id, key, func, *args, **kwargs):
        """ Get key for id=item_id in table else set key to func(*args, **kwargs) """
        value = self.get_cached(table, item_id, key)
        if not value:
            value = func(*args, **kwargs)
            value = self.set_cached(table, item_id, key, value)
        return value

    # =========================================
    # Single item with multiple key/value pairs
    # =========================================

    def set_cached_values(self, table, item_id, keys, values):
        return self.cache.set_item_values(table, item_id, keys, values, connection=self.connection)

    # ============================================
    # Multiple items with multiple key/value pairs
    # ============================================

    def get_cached_list_values(self, table, keys, values, conditions):
        return self.cache.get_list_values(table, keys, values, conditions, connection=self.connection)

    def set_cached_list_values(self, table, keys, values):
        return self.cache.set_list_values(table, keys, values, connection=self.connection)

    def set_cached_many(self, table, keys, data):
        if not data:
            return
        self.cache.set_many_values(table, keys, data, connection=self.connection)
        return data

    def use_cached_many(self, table, keys, values, conditions, func, *args, **kwargs):
        data = self.get_cached_list_values(table, keys, values, conditions)
        if not data:
            data = self.set_cached_many(table, keys, func(*args, **kwargs))
            data = self.get_cached_list_values(table, keys, values, conditions) if data else None
        return data
