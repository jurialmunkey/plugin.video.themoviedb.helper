from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.basemedia import MediaItem
from jurialmunkey.ftools import cached_property


class Movie(MediaItem):
    table = 'movie'
    tmdb_type = 'movie'
    ftv_type = 'movies'

    @cached_property
    def online_data_collection(self):
        if self.cache_refresh == 'basic':
            return {}
        if not self.online_data_tmdb:
            return {}
        if not self.online_data_tmdb.get('belongs_to_collection'):
            return {}
        args = ('collection', self.online_data_tmdb['belongs_to_collection']['id'])
        return self.online_data_func(*args) or {}

    @cached_property
    def online_data_combined(self):
        data = self.online_data_tmdb
        data['fanart_tv'] = self.online_data_ftv
        data['collection'] = self.online_data_collection
        return data

    @property
    def cached_data_table(self):
        """ FROM """
        return (
            f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id '
            f'LEFT JOIN belongs ON belongs.id = {self.table}.id '
            f'LEFT JOIN collection ON collection.id = belongs.parent_id '
        )

    @property
    def cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys]
        cached_data_keys.extend([
            'collection.title AS collection_title',
            'collection.tmdb_id AS collection_tmdb_id',
            'collection.id AS collection_id',
            (
                '(  SELECT art.icon FROM art'
                '   WHERE art.parent_id=collection.id AND type=\'posters\' '
                '   ORDER BY '
                f'           iso_language=\'{self.common_apis.tmdb_api.iso_language}\' DESC, '
                '            iso_language=\'en\' DESC, '
                '            iso_language IS NULL DESC, '
                '            rating DESC'
                '   LIMIT 1'
                ') as collection_poster'
            ),
            (
                '(  SELECT art.icon FROM art'
                '   WHERE art.parent_id=collection.id AND type=\'backdrops\' AND iso_language IS NULL'
                '   ORDER BY rating DESC LIMIT 1'
                ') as collection_fanart'
            ),
        ])
        return tuple(cached_data_keys)

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('collection'),
            self.return_basemeta_db('movie'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
            self.return_basemeta_db('translation'),
            self.return_basemeta_db('video'),
            self.return_basemeta_db('company'),
            self.return_basemeta_db('studio'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('fanart_tv'),
            self.return_basemeta_db('art'),

        )
