from tmdbhelper.lib.files.dbdata import Database
from tmdbhelper.lib.files.dbfunc import DatabaseAccess
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY
from tmdbhelper.lib.query.database.genres import FindQueriesDatabaseGenres
from tmdbhelper.lib.query.database.tmdb_id import FindQueriesDatabaseTMDbID
from tmdbhelper.lib.query.database.certification import FindQueriesDatabaseCertification
from tmdbhelper.lib.query.database.provider_regions import FindQueriesDatabaseProviderRegions
from tmdbhelper.lib.query.database.watch_providers import FindQueriesDatabaseWatchProviders
from tmdbhelper.lib.query.database.collections import FindQueriesDatabaseCollections
from tmdbhelper.lib.query.database.keywords import FindQueriesDatabaseKeywords
from tmdbhelper.lib.query.database.studios import FindQueriesDatabaseStudios
from tmdbhelper.lib.query.database.networks import FindQueriesDatabaseNetworks
from tmdbhelper.lib.query.database.movies import FindQueriesDatabaseMovies
from tmdbhelper.lib.query.database.tvshows import FindQueriesDatabaseTvshows
from tmdbhelper.lib.query.database.imdb_top250 import FindQueriesDatabaseIMDbTop250
from tmdbhelper.lib.query.database.trakt_id import FindQueriesDatabaseTraktID
from tmdbhelper.lib.query.database.trakt_stats import FindQueriesDatabaseTraktStats
from tmdbhelper.lib.query.database.identifier import FindQueriesDatabaseIdentifier
from tmdbhelper.lib.query.database.user_ratings import FindQueriesDatabaseUserRatings


class FindQueriesDatabase(
    Database,
    FindQueriesDatabaseGenres,
    FindQueriesDatabaseTMDbID,
    FindQueriesDatabaseCertification,
    FindQueriesDatabaseProviderRegions,
    FindQueriesDatabaseWatchProviders,
    FindQueriesDatabaseCollections,
    FindQueriesDatabaseKeywords,
    FindQueriesDatabaseStudios,
    FindQueriesDatabaseNetworks,
    FindQueriesDatabaseMovies,
    FindQueriesDatabaseTvshows,
    FindQueriesDatabaseIMDbTop250,
    FindQueriesDatabaseTraktID,
    FindQueriesDatabaseTraktStats,
    FindQueriesDatabaseIdentifier,
    FindQueriesDatabaseUserRatings,
):
    cache_filename = 'ItemQueries.db'

    expiry_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True
        },
        'expiry': {
            'data': 'INTEGER'
        },
    }

    database_version = 4

    database_changes = {
        2: (
            'DROP TABLE IF EXISTS genres',
        ),
        3: (),
        4: (
            'DROP TABLE IF EXISTS trakt_id',
        )
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
            'imdb_top250': self.imdb_top250_columns,
            'trakt_id': self.trakt_id_columns,
            'trakt_stats': self.trakt_stats_columns,
            'identifier': self.identifier_columns,
            'user_ratings': self.user_ratings_columns,
        }

    def __init__(self):
        super().__init__(filename=self.cache_filename)

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def tmdb_user_api(self):
        from tmdbhelper.lib.api.tmdb.users import TMDbUser
        return TMDbUser()

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
