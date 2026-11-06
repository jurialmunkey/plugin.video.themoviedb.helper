#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.addon.logger import kodi_log, TimerFunc
from tmdbhelper.lib.addon.plugin import get_setting, get_version
from tmdbhelper.lib.files.futils import FileUtils
from contextlib import closing, contextmanager
import sqlite3
import struct


DEFAULT_TABLE = 'simplecache'
DATABASE_NAME = 'database_07'


class _SQLResourceError(Exception):
    """Keep fetch and cleanup errors from being swallowed by the cache wrapper."""

    def __init__(self, original):
        self.original = original
        super().__init__(str(original))


class DatabaseCore:
    _basefolder = get_setting('cache_location', 'str') or ''
    _fileutils = FileUtils()  # Import to use plugin addon_data folder not the module one
    _db_timeout = 60.0
    _db_read_timeout = 1.0
    # Large SQLite mappings can exhaust the address space on 32-bit Kodi.
    _db_mmap_size = 0 if struct.calcsize('P') == 4 else 256 * 1024 * 1024
    database_version = 1
    database_changes = {}

    def __init__(self, folder=None, filename=None):
        '''Initialize our caching class'''
        folder = folder or DATABASE_NAME
        basefolder = f'{self._basefolder}{folder}'
        filename = filename or 'defaultcache.db'

        self._db_file = self._fileutils.get_file_path(basefolder, filename, join_addon_data=basefolder == folder)
        self._sc_name = f'{folder}_{filename}_databaserowfactory_{get_version()}'
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
        for pragma in (
            "PRAGMA synchronous=NORMAL",
            "PRAGMA journal_mode=WAL",
            "PRAGMA foreign_keys=ON",
            f"PRAGMA mmap_size={self._db_mmap_size}",
        ):
            connection.execute(pragma).close()
        return connection

    def init_database(self):
        from jurialmunkey.locker import MutexPropLock
        with MutexPropLock(f'{self._db_file}.lockfile', kodi_log=self.kodi_log):
            if self.create_database():
                self.set_database_init()
                return True
        return False

    def create_database(self):
        try:
            with TimerFunc(f'CACHE: Initialisation {self._db_file} took:'):
                self.kodi_log(f'CACHE: Initialising...\n{self._db_file}\n{self._sc_name}', 1)
                with closing(sqlite3.connect(self._db_file, timeout=self._db_timeout)) as connection:
                    self.set_pragmas(connection)
                    with connection:
                        self.create_database_execute(connection)
            return True
        except Exception as error:
            self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name}', 1)
            return False

    def get_database(self, read_only=False, log_level=1):
        timeout = self._db_read_timeout if read_only else self._db_timeout
        try:
            connection = sqlite3.connect(self._db_file, timeout=timeout)
        except Exception as error:
            self.kodi_log(f'CACHE: ERROR while retrieving _database: {error}\n{self._sc_name}', log_level)
            return
        try:
            connection.row_factory = sqlite3.Row
            return self.set_pragmas(connection)
        except Exception:
            # Keep the setup error if closing the connection also fails.
            try:
                connection.close()
            except Exception as close_error:
                self._log_cleanup_error(
                    close_error, prefix='CACHE: ERROR while closing failed _database setup')
            raise

    @contextmanager
    def database_session(self, read_only=False, wrap_resource_errors=False):
        connection = self.get_database(read_only=read_only)
        if connection is None:
            raise sqlite3.OperationalError('Database connection unavailable')
        try:
            with connection:
                yield connection
        except BaseException:
            try:
                connection.close()
            except BaseException as error:
                self._log_cleanup_error(error)
            raise
        else:
            try:
                connection.close()
            except Exception as error:
                if wrap_resource_errors:
                    raise _SQLResourceError(error) from error
                raise

    def _log_cleanup_error(self, error, prefix='CACHE: ERROR closing _database'):
        try:
            self.kodi_log(f'{prefix}: {error}\n{self._sc_name}', 2)
        except Exception:
            pass

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

    def _execute_sql(
            self, query, data=None, read_only=False, connection=None,
            fetch_rows=None, wrap_resource_errors=False):
        """Fetch results before closing connections opened here.

        Callers providing their own connection keep control of the cursor.
        """
        if connection is not None:
            return self.database_execute(connection, query, data=data)
        with self.database_session(
                read_only=read_only, wrap_resource_errors=wrap_resource_errors) as database:
            cursor = self.database_execute(database, query, data=data)
            if cursor is None:
                return
            failed = False
            try:
                should_fetch = read_only if fetch_rows is None else fetch_rows
                if should_fetch:
                    try:
                        return cursor.fetchall()
                    except Exception as error:
                        if wrap_resource_errors:
                            raise _SQLResourceError(error) from error
                        raise
            except BaseException:
                failed = True
                raise
            finally:
                try:
                    cursor.close()
                except Exception as close_error:
                    if failed:
                        # Don't replace a fetch error if closing the cursor also fails.
                        self._log_cleanup_error(
                            close_error, prefix='CACHE: cursor close error after failed query')
                    elif wrap_resource_errors:
                        raise _SQLResourceError(close_error) from close_error
                    else:
                        raise

    def execute_sql(self, query, data=None, read_only=False, connection=None, fetch_rows=None):
        try:
            return self._execute_sql(
                query, data=data, read_only=read_only, connection=connection,
                fetch_rows=fetch_rows, wrap_resource_errors=True)
        except _SQLResourceError as error:
            raise error.original from error
        except Exception as database_exception:
            self.kodi_log(f'CACHE: database GET DATABASE ERROR! -- {database_exception}\n{self._sc_name} -- read_only: {read_only}', 2)

    @property
    def database_tables(self):
        return {}

    def create_database_execute(self, connection):

        def create_column_data(columns):
            return [
                f'{k} {v["data"]}'
                for k, v in columns.items()
            ]

        def create_column_fkey(columns):
            return [
                f'FOREIGN KEY({k}) REFERENCES {v["foreign_key"]} ON DELETE CASCADE'
                for k, v in columns.items()
                if 'foreign_key' in v
            ]

        def create_column_uids(columns):
            keys = [
                k for k, v in columns.items()
                if v.get('unique')
            ]
            if not keys:
                return []
            return ['UNIQUE ({})'.format(', '.join(keys))]

        cursor = connection.cursor()
        this_database_version = cursor.execute("PRAGMA user_version").fetchone()[0]

        # OLD DATABASE SCHEME: APPLY MODIFICATIONS
        if this_database_version and this_database_version < self.database_version:
            for version, changes in self.database_changes.items():
                if version <= this_database_version:
                    continue
                for query in changes:
                    try:
                        cursor.execute(query)
                    except Exception as error:
                        self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        # CREATE TABLES IF NOT EXISTS
        for table, columns in self.database_tables.items():
            query = []
            query += create_column_data(columns)
            query += create_column_fkey(columns)
            query += create_column_uids(columns)
            query = 'CREATE TABLE IF NOT EXISTS {table}({query})'.format(table=table, query=', '.join(query))
            try:
                cursor.execute(query)
            except Exception as error:
                self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        # CREATE INDICIES
        for table, columns in self.database_tables.items():
            for column, v in columns.items():
                if not v.get('indexed'):
                    continue
                query = 'CREATE INDEX IF NOT EXISTS {table}_{column}_x ON {table}({column})'.format(table=table, column=column)
                try:
                    cursor.execute(query)
                except Exception as error:
                    self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        # DO SOME DATABASE MAINTAINENCE IF DB VERSION INCREASED
        if this_database_version < self.database_version:
            # UPDATE DATABASE VERSION
            try:
                query = f"PRAGMA user_version = {self.database_version}"
                cursor.execute(query)
            except Exception as error:
                self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        return connection


class DatabaseStatements:
    @staticmethod
    def insert_or_ignore(table, keys=('id', )):
        return 'INSERT OR IGNORE INTO {table}({keys}) VALUES ({values})'.format(
            table=table,
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]))

    @staticmethod
    def insert_or_replace(table, keys=('id', )):
        return 'INSERT OR REPLACE INTO {table}({keys}) VALUES ({values})'.format(
            table=table,
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]))

    @staticmethod
    def insert_or_update_if_null(table, keys=('id', ), conflict_constraint='id'):
        conflict_keys = tuple(k.strip() for k in conflict_constraint.split(','))
        update_keys = ', '.join(
            f'{k}=ifnull({k},excluded.{k})' for k in keys if k not in conflict_keys)
        update_clause = f'DO UPDATE SET {update_keys}' if update_keys else 'DO NOTHING'
        return (
            'INSERT INTO {table}({keys}) VALUES ({values}) '
            'ON CONFLICT ({conflict_constraint}) {update_clause} '
        ).format(
            table=table,
            keys=', '.join(keys),
            values=', '.join(['?' for _ in keys]),
            conflict_constraint=conflict_constraint,
            update_clause=update_clause
        )

    @staticmethod
    def delete_keys(table, keys, conditions='item_type=?'):
        return 'UPDATE {table} SET {keys} {conditions}'.format(
            table=table,
            keys=', '.join([f'{k}=NULL' for k in keys]),
            conditions=f'WHERE {conditions}' if conditions else '')

    @staticmethod
    def delete_item(table, conditions='id=?'):
        return 'DELETE FROM {table} WHERE {conditions}'.format(
            table=table,
            conditions=conditions)

    @staticmethod
    def update_if_null(table, keys, conditions='id=?'):
        return 'UPDATE {table} SET {keys} WHERE {conditions}'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]), table=table, conditions=conditions)

    @staticmethod
    def select_limit(table, keys, conditions='id=?'):
        return 'SELECT {keys} FROM {table} WHERE {conditions} LIMIT 1'.format(
            keys=', '.join(keys), table=table, conditions=conditions)

    @staticmethod
    def select(table, keys, conditions=None):
        if not conditions:
            return 'SELECT {keys} FROM {table}'.format(
                keys=', '.join(keys), table=table)
        return 'SELECT {keys} FROM {table} WHERE {conditions}'.format(
            keys=', '.join(keys), table=table, conditions=conditions)


class DatabaseMethod:
    def set_list_values(self, table=DEFAULT_TABLE, keys=(), values=(), overwrite=False, connection=None):
        if not values:
            return
        statement = (
            DatabaseStatements.insert_or_ignore
            if not overwrite else
            DatabaseStatements.insert_or_replace
        )
        self.execute_sql(
            statement(table, keys),
            values,
            connection=connection)

    def get_list_values(self, table=DEFAULT_TABLE, keys=(), values=(), conditions=None, connection=None):
        result = self.execute_sql(
            DatabaseStatements.select(table, keys, conditions),
            data=values,
            read_only=True,
            connection=connection)
        if connection is None:
            return result
        return result.fetchall() if result is not None else None

    def del_list_values(self, table=DEFAULT_TABLE, values=(), conditions=None, connection=None):
        self.execute_sql(
            DatabaseStatements.delete_item(table, conditions),
            data=values,
            connection=connection)

    def set_or_update_null_list_values(self, table=DEFAULT_TABLE, keys=(), values=(), conflict_constraint='id', connection=None):
        if not values:
            return
        statement = DatabaseStatements.insert_or_update_if_null
        self.execute_sql(
            statement(table, keys, conflict_constraint=conflict_constraint),
            values,
            connection=connection)

    def get_values(self, table=DEFAULT_TABLE, item_id=None, keys=(), connection=None):
        result = self.execute_sql(
            DatabaseStatements.select_limit(table, keys),
            data=(item_id, ),
            read_only=True,
            connection=connection)
        if connection is None:
            return result[0] if result else None
        return result.fetchone() if result is not None else None

    def set_item_values(self, table=DEFAULT_TABLE, item_id=None, keys=(), values=(), connection=None):
        """ Create a new row at id=item_id (or update if it exists) and then update null values with new data """
        self.create_item(
            table=table,
            item_id=item_id,
            connection=connection)

        self.execute_sql(
            DatabaseStatements.update_if_null(table, keys),
            data=(*values, item_id, ),
            connection=connection)

    def set_many_values(self, table=DEFAULT_TABLE, keys=(), data=None, connection=None):
        """ data={item_id: ((key, value), (key, value))} """

        # Create new rows if items dont exist
        self.create_many_items(
            table=table,
            item_ids=[item_id for item_id in data.keys()],
            connection=connection)

        self.execute_sql(
            DatabaseStatements.update_if_null(table, keys),
            data=[(*values, item_id, ) for item_id, values in data.items()],
            connection=connection)

    def del_column_values(self, table=DEFAULT_TABLE, keys=(), item_type=None, connection=None):
        self.execute_sql(
            DatabaseStatements.delete_keys(
                table, keys,
                conditions=None if item_type is None else 'item_type=?'),
            data=None if item_type is None else (item_type, ),
            connection=connection)

    def del_item(self, table=DEFAULT_TABLE, item_id=None, connection=None):
        self.execute_sql(
            DatabaseStatements.delete_item(table),
            data=(item_id, ),
            connection=connection)

    def del_item_like(self, table=DEFAULT_TABLE, item_id=None, connection=None):
        self.execute_sql(
            DatabaseStatements.delete_item(table, conditions='id LIKE ?'),
            data=(item_id, ),
            connection=connection)

    def create_item(self, table=DEFAULT_TABLE, item_id=None, connection=None):
        self.execute_sql(
            DatabaseStatements.insert_or_ignore(table),
            data=(item_id,),
            connection=connection)

    def create_many_items(self, table=DEFAULT_TABLE, item_ids=(), connection=None):
        self.execute_sql(
            DatabaseStatements.insert_or_ignore(table),
            data=[(item_id,) for item_id in item_ids],
            connection=connection)


class Database(DatabaseCore, DatabaseMethod):
    pass
