from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem


class Series(BaseItem):
    table = 'collection'
    tmdb_type = 'collection'
    ftv_id = None
    append_to_response_tmdbtype = 'collection'
    append_to_response_extended = False
    append_to_response_language = False

    @property
    def cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys]
        return tuple(cached_data_keys)

    @staticmethod
    def set_unaired_expiry(*args, **kwargs):
        return  # Collections dont have premiered dates so we dont modify expiry time

    @property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('collection'),
            self.return_basemeta_db('movie'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('default_art'),
            self.return_basemeta_db('art'),
        )
