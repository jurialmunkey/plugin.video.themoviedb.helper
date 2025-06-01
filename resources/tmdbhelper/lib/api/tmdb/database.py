from tmdbhelper.lib.files.dbdata import Database
from tmdbhelper.lib.files.dbfunc import DatabaseAccess
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY
from tmdbhelper.lib.api.tmdb.database_tables.genres import TMDbDatabaseGenres
from tmdbhelper.lib.api.tmdb.database_tables.tmdb_id import TMDbDatabaseTMDbID
from tmdbhelper.lib.api.tmdb.database_tables.certification import TMDbDatabaseCertification
from tmdbhelper.lib.api.tmdb.database_tables.provider_regions import TMDbDatabaseProviderRegions
from tmdbhelper.lib.api.tmdb.database_tables.watch_providers import TMDbDatabaseWatchProviders
from tmdbhelper.lib.api.tmdb.database_tables.collections import TMDbDatabaseCollections
from tmdbhelper.lib.api.tmdb.database_tables.keywords import TMDbDatabaseKeywords
from tmdbhelper.lib.api.tmdb.database_tables.studios import TMDbDatabaseStudios
from tmdbhelper.lib.api.tmdb.database_tables.networks import TMDbDatabaseNetworks
from tmdbhelper.lib.api.tmdb.database_tables.movies import TMDbDatabaseMovies
from tmdbhelper.lib.api.tmdb.database_tables.tvshows import TMDbDatabaseTvshows


class TMDbDatabase(
    Database,
    TMDbDatabaseGenres,
    TMDbDatabaseTMDbID,
    TMDbDatabaseCertification,
    TMDbDatabaseProviderRegions,
    TMDbDatabaseWatchProviders,
    TMDbDatabaseCollections,
    TMDbDatabaseKeywords,
    TMDbDatabaseStudios,
    TMDbDatabaseNetworks,
    TMDbDatabaseMovies,
    TMDbDatabaseTvshows,
):
    cache_filename = 'LookupTMDb.db'

    expiry_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True
        },
        'expiry': {
            'data': 'INTEGER'
        },
    }

    @property
    def database_tables(self):
        return {
            'expiry': self.expiry_columns,
            'genres': self.genres_columns,
            'tmdb_id': self.tmdb_id_columns,
            'certification': self.certification_columns,
            'provider_regions': self.provider_regions_columns,
            'watch_providers': self.watch_providers_columns,
            'watch_providers_details': self.watch_providers_details_columns,
            'collections': self.collections_columns,
            'keywords': self.keywords_columns,
            'studios': self.studios_columns,
            'networks': self.networks_columns,
            'movies': self.movies_columns,
            'tvshows': self.tvshows_columns,
        }

    def __init__(self):
        super().__init__(filename=self.cache_filename)

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def access(self):
        access = DatabaseAccess()
        access.cache = self
        return access

    @property
    def current_time(self):
        return set_timestamp(0, set_int=True)

    def is_expired(self, item_id):
        expiry = self.access.get_cached(table='expiry', item_id=item_id, key='expiry') or 0
        return bool(self.current_time >= expiry)

    def set_expiry(self, item_id, expiry=DEFAULT_EXPIRY):
        self.access.set_cached('expiry', item_id, 'expiry', self.current_time + expiry)

    def get_item_values(self, table, item_id, keys):
        return self.access.get_cached_values(table, item_id, keys=keys)

    def get_cached_item_values(self, table, item_id, keys, mapping_function=None):
        data = None
        with self.access.connection.open():
            if not self.is_expired(f'{table}.{item_id}'):
                data = self.get_item_values(table, item_id, keys=keys)
        return mapping_function(data) if mapping_function else data

    def get_all_values(self, table, keys, values=None, conditions=None):
        return self.access.get_cached_list_values(table, keys=keys, values=values or (), conditions=conditions)

    def get_cached_values(self, table, keys, mapping_function=None, values=None, conditions=None):
        data = None
        with self.access.connection.open():
            if not self.is_expired(table):
                data = self.get_all_values(
                    table,
                    keys=keys,
                    values=values,
                    conditions=conditions)
        return mapping_function(data) if mapping_function else data

    def set_cached_values(self, table, keys, values, item_id=None, expiry=DEFAULT_EXPIRY, overwrite=True):
        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            self.set_expiry(f'{table}.{item_id}' if item_id else table, expiry=expiry) if expiry else None
            self.access.set_cached_list_values(table, keys=keys, values=values, overwrite=overwrite)
            connection.execute('COMMIT')
