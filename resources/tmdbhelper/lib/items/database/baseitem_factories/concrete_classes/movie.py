from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.files.ftools import cached_property


class Movie(MediaItem):
    table = 'movie'
    tmdb_type = 'movie'
    ftv_type = 'movies'

    @property
    def cached_data_table(self):
        """ FROM """
        return (
            f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id '
            f'LEFT JOIN collection ON collection.id = {self.table}.collection_id '
        )

    @property
    def cached_data_keys(self):
        """ SELECT """
        additional_keys = [
            'collection.title AS collection_title',
            'collection.poster AS collection_poster',
            'collection.fanart AS collection_fanart',
            'collection.tmdb_id AS collection_tmdb_id',
        ]
        return tuple([f'{self.table}.{k}' for k in self.keys] + additional_keys)

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('collection'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
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
