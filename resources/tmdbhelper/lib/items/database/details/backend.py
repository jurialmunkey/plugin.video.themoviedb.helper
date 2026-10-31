from contextlib import contextmanager
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.dbfunc import DatabaseConnection
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.items.database.details.apis import DetailsAPIs


class DetailsDatabase(ItemDetailsDatabase):
    def __init__(self):
        self._basefolder = get_setting('cache_location', 'str') or ''
        super().__init__()

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


class DetailsLookup:
    """Configure a fresh factory before accessing any cached factory properties."""

    def __init__(self, cache, request, common_apis, connection=None, parent_data=None):
        self.request = request
        self.common_apis = common_apis
        self.owns_connection = connection is None
        self.factory = BaseItemFactory(request.mediatype, common_apis=self.common_apis)
        self.factory.cache = cache
        self.factory.connection = connection or DetailsConnection(cache)
        for name in (
                'tmdb_id', 'season', 'episode', 'cache_refresh',
                'cache_translations', 'extendedinfo'):
            setattr(self.factory, name, getattr(request, name))
        if request.tvshow_tmdb_id is not None:
            self.factory.tvshow_tmdb_id = request.tvshow_tmdb_id
        self.factory.parent_item_data = parent_data

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
    def __init__(self):
        self.apis = DetailsAPIs()

    @cached_property
    def cache(self):
        return DetailsDatabase()

    @cached_property
    def connection(self):
        return DetailsConnection(self.cache)

    def lookup(self, request, parent_data=None):
        return DetailsLookup(
            self.cache, request, self.apis.get(request.language),
            self.connection, parent_data)

    def read(self, request):
        lookup = self.lookup(request)
        return lookup.get_cached_data()

    def fetch(self, request, parent_data):
        lookup = DetailsLookup(
            self.cache, request, self.apis.get(request.language), parent_data=parent_data)
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
        try:
            self.connection.close()
        finally:
            self.apis.close()
