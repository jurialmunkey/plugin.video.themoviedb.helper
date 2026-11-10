from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.basemeta_factories.factory import BaseMetaFactory
from tmdbhelper.lib.query.database.table import FindQueriesDatabaseTable


class FindQueriesDatabaseTableExternalIds(FindQueriesDatabaseTable):
    table = 'external_ids'
    keys = (
        'id', 'tmdb_type', 'parent_tmdb_id', 'season', 'episode',
        'tmdb_id', 'imdb_id', 'tvdb_id')
    conditions = 'id=?'
    season = None
    episode = None
    metadata_id_requirements = {'movie': ('imdb',), 'tv': ('imdb', 'tvdb')}

    @cached_property
    def item_id(self):
        return self.get_item_id()

    def get_item_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}'

    @property
    def values(self):
        return (self.item_id,)

    @property
    def expiry_id(self):
        return f'{self.table}.{self.item_id}'

    @property
    def request_path(self):
        return (self.tmdb_type, self.tmdb_id)

    @property
    def request_args(self):
        return (*self.request_path, 'external_ids')

    def statement_mapping(self, data):
        return (
            self.item_id, self.tmdb_type, self.tmdb_id, self.season, self.episode,
            data['id'], data.get('imdb_id'), data.get('tvdb_id'))

    @staticmethod
    def get_mapping(data):
        if not data:
            return {}
        row = data[0]
        return {
            key: row[f'{key}_id'] for key in ('tmdb', 'imdb', 'tvdb')
            if row[f'{key}_id'] not in (None, '')}

    def get_metadata_ids(self):
        reader = BaseMetaFactory('external_ids')
        reader.item_id = self.item_id
        return reader.ids

    def get_response_mapping(self, data):
        row = dict(zip(self.keys, self.statement_mapping(data)))
        return self.get_mapping((row,))

    def use(self):
        metadata_ids = self.get_metadata_ids()
        if all(metadata_ids.get(key) for key in self.metadata_id_requirements[self.tmdb_type]):
            return metadata_ids
        return dict(super().use() or {}, **metadata_ids)

    def set(self):
        with self.access.connection.open():
            if not self.is_expired_set:
                return
        data = self.tmdb_api.get_response_json(*self.request_args, **self.request_kwgs)
        if not data:  # Failed requests must not refresh the cache expiry.
            return
        mapped = self.get_response_mapping(data)
        self.set_response(data)
        return mapped

    def set_response(self, data):
        statements = [item.statement(item.table, item.keys) for item in self.insert_statements]
        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            self.set_tables(connection, statements, (data,))
            self.set_expiry(self.expiry_id)
            connection.execute('COMMIT')


class FindQueriesDatabaseTableSeasonExternalIds(FindQueriesDatabaseTableExternalIds):
    def get_item_id(self):
        return f'{super().get_item_id()}.{self.season}'

    @property
    def request_path(self):
        return (*super().request_path, 'season', self.season)


class FindQueriesDatabaseTableEpisodeExternalIds(FindQueriesDatabaseTableSeasonExternalIds):
    def get_item_id(self):
        return f'{super().get_item_id()}.{self.episode}'

    @property
    def request_path(self):
        return (*super().request_path, 'episode', self.episode)


class FindQueriesDatabaseExternalIds:
    external_ids_columns = {
        'id': {'data': 'TEXT PRIMARY KEY'},
        'tmdb_type': {'data': 'TEXT'},
        'parent_tmdb_id': {'data': 'INTEGER'},
        'season': {'data': 'INTEGER'},
        'episode': {'data': 'INTEGER'},
        'tmdb_id': {'data': 'INTEGER', 'indexed': True},
        'imdb_id': {'data': 'TEXT'},
        'tvdb_id': {'data': 'TEXT'},
    }

    def get_external_ids(self, tmdb_type, tmdb_id, season=None, episode=None):
        table_class = (
            FindQueriesDatabaseTableEpisodeExternalIds if episode is not None else
            FindQueriesDatabaseTableSeasonExternalIds if season is not None else
            FindQueriesDatabaseTableExternalIds)
        table = table_class(self)
        table.tmdb_type = tmdb_type
        table.tmdb_id = tmdb_id
        table.season = season
        table.episode = episode
        return table.use()
