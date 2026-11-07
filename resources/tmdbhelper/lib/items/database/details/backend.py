import sqlite3
from contextlib import contextmanager
from threading import Lock, local
from jurialmunkey.ftools import cached_property, threaded_cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.dbfunc import DatabaseConnection
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.items.database.details.apis import DetailsAPIs
from tmdbhelper.lib.items.database.details.metadata import DetailsMetadataCache


class DetailsDatabase(ItemDetailsDatabase):
    def __init__(self):
        self._basefolder = get_setting('cache_location', 'str') or ''
        super().__init__()

    def get_shared_database(self, read_only=False):
        """Open a connection that one thread uses at a time and another thread may close."""
        timeout = self._db_read_timeout if read_only else self._db_timeout
        connection = sqlite3.connect(self._db_file, timeout=timeout, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return self.set_pragmas(connection)

    def database_execute(self, connection, query, data=None):
        # The coordinator must roll back and restart on database errors. Treating
        # an unsuccessful statement as a cache miss could commit a partial item.
        if not data:
            return connection.execute(query)
        if isinstance(data, list):
            return connection.executemany(query, data)
        return connection.execute(query, data)

    def execute_sql(self, query, data=None, read_only=False, connection=None):
        if connection is not None:
            return self.database_execute(connection, query, data)
        with self.get_database(read_only=read_only) as connection:
            return self.database_execute(connection, query, data)


class DetailsConnection(DatabaseConnection):
    """Own both the cursor and connection, including rollback on failed batches."""

    @classmethod
    def get_shared(cls, cache):
        """Keep a connection open that one thread uses at a time and another thread may close."""
        connection = cls(cache)
        connection.open_connection = cache.get_shared_database().cursor()
        return connection

    def close(self):
        if self.open_connection is None:
            return
        connection = self.open_connection.connection
        try:
            super().close()
        finally:
            connection.close()

    @contextmanager
    def open(self):
        existing_connection = self.open_connection is not None
        if not existing_connection:
            self.open_connection = self.cache.get_database().cursor()
        try:
            yield self.open_connection
        finally:
            if not existing_connection:
                self.close()


class DetailsReaderConnections:
    """Keep one open connection per reader thread, as DetailsAPIs keeps one API context."""

    def __init__(self, cache):
        self.cache = cache
        self.local = local()
        self.lock = Lock()
        self.connections = set()

    def get(self):
        try:
            return self.local.connection
        except AttributeError:
            pass
        connection = self.local.connection = self.get_connection()
        with self.lock:
            self.connections.add(connection)
        return connection

    def get_connection(self):
        return DetailsConnection.get_shared(self.cache)

    def close(self):
        """Close after the reader threads have stopped."""
        with self.lock:
            connections, self.connections = self.connections, set()
        for connection in connections:
            connection.close()


class DetailsLookup:
    """Configure a fresh factory before accessing any cached factory properties."""

    item_factory = staticmethod(BaseItemFactory)

    def __init__(
            self, cache, request, common_apis, connection=None, parent_data=None,
            sync_enabled=True, metadata_cache=None):
        self.request = request
        self.common_apis = common_apis
        self.owns_connection = connection is None
        self.factory = self.item_factory(request.mediatype, common_apis=self.common_apis)
        self.factory.cache = cache
        self.factory.connection = connection or DetailsConnection(cache)
        for name in (
                'tmdb_id', 'season', 'episode', 'cache_refresh',
                'cache_translations', 'extendedinfo'):
            setattr(self.factory, name, getattr(request, name))
        if request.tvshow_tmdb_id is not None:
            self.factory.tvshow_tmdb_id = request.tvshow_tmdb_id
        self.factory.sync_details = bool(request.sync_details and sync_enabled)
        self.factory.parent_item_data = parent_data
        self.factory.metadata_cache = metadata_cache

    @property
    def key(self):
        return (
            self.request.identity, self.factory.datalevel,
            self.factory.translation, self.factory.fanart_tv,
            self.request.cache_refresh == 'force', self.request.clear_user_art,
        )

    def get_cached_data(self):
        data = self.factory.get_cached_data()
        if data:
            data['infoproperties'].update({
                'dbtype': self.request.mediatype,
                'tmdb_type': self.factory.tmdb_type,
                'tmdb_id': self.request.tmdb_id,
            })
            data['label'] = data['infolabels']['title']
        return data

    def close(self):
        if self.owns_connection:
            self.factory.connection.close()


class DetailsBackend:
    lookup_class = DetailsLookup

    def __init__(self):
        self.apis = DetailsAPIs()

    @cached_property
    def cache(self):
        return DetailsDatabase()

    @cached_property
    def connection(self):
        return DetailsConnection(self.cache)

    @threaded_cached_property
    def reader_connections(self):
        return DetailsReaderConnections(self.cache)

    @threaded_cached_property
    def metadata_cache(self):
        return DetailsMetadataCache(self.cache)

    @threaded_cached_property
    def is_sync_enabled(self):
        """Settings changes restart the service, so the setting is read once."""
        from tmdbhelper.lib.sync.prepare import SyncPreparation
        return SyncPreparation.is_enabled()

    def lookup(self, request, parent_data=None, connection=None):
        return self.lookup_class(
            self.cache, request, self.apis.get(request.language),
            self.connection if connection is None else connection,
            parent_data, sync_enabled=self.is_sync_enabled,
            metadata_cache=self.metadata_cache)

    def read(self, request, connection=None):
        lookup = self.lookup(request, connection=connection)
        return lookup.get_cached_data()

    def read_worker(self, request):
        """Read on a reader thread through that thread's own connection."""
        return self.read(request, self.reader_connections.get())

    def fetch(self, request, parent_data):
        lookup = self.lookup_class(
            self.cache, request, self.apis.get(request.language),
            parent_data=parent_data, sync_enabled=self.is_sync_enabled)
        try:
            if not lookup.factory.data_cond:
                return []
            return lookup.factory.try_cached_data(return_queue=True) or []
        finally:
            lookup.close()

    def commit(self, request, queue):
        # A basic lookup may have finished after a richer lookup populated the row.
        # Keep the richer records rather than replacing them with the basic response.
        if request.cache_refresh != 'force' and self.read(request) is not None:
            return
        with self.connection.open() as cursor:
            cursor.execute('BEGIN')
            try:
                if request.clear_user_art:
                    self.clear_user_art(request)
                for func, args, kwargs in queue:
                    func.__self__.connection = self.connection
                for func, args, kwargs in queue:
                    func(*args, **kwargs)
                cursor.execute('COMMIT')
            except BaseException:
                cursor.execute('ROLLBACK')
                raise
        self.metadata_cache.discard_saved(self.lookup(request).factory)

    def clear_user_art(self, request):
        lookup = self.lookup(request)
        item_id = lookup.factory.item_id
        self.cache.del_list_values(
            table='user_art', values=(item_id, f'{item_id}.%'),
            conditions='parent_id=? OR parent_id LIKE ?',
            connection=self.connection.open_connection)

    def fallback(self, request):
        lookup = self.lookup(request)
        return lookup.factory.get_lookup_fallback()

    def close(self):
        # Reader threads have stopped before the backend closes.
        self.close_created(('connection', 'reader_connections', 'metadata_cache', 'apis'))

    def close_created(self, names):
        """Close each created resource in order, even when an earlier close fails."""
        if not names:
            return
        try:
            if names[0] in self.__dict__:
                self.__dict__[names[0]].close()
        finally:
            self.close_created(names[1:])
