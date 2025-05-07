from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.basedata import ItemDetailsDatabaseAccess


class BaseList(ItemDetailsDatabaseAccess):
    cached_data_check_key = 'expiry'
    cache_refresh = None  # Set to "never" for cache only, or "force" for forced refresh
    cached_data_table = table = 'baseitem'
    cached_data_conditions = 'id=? AND expiry>=?'

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        return bool(self.tmdb_id)

    @cached_property
    def item_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @property
    def cached_data_keys(self):
        """ SELECT """
        return tuple((f'{self.table}.{k}' for k in self.keys))

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        if self.cache_refresh == 'never':
            return (self.item_id, 0, )
        return (self.item_id, self.current_time, )

    def configure_mapped_data(self, data):
        def get_value(k):
            if k == 'id':
                return self.item_id
            if k == 'expiry':
                return self.expiry
            try:
                return data[k]
            except (TypeError, KeyError, IndexError, ValueError):
                return
        return [get_value(k) for k in self.keys]

    def db_baseitem_cache_get_parent_data(self):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        base_dbc = BaseItemFactory(self.mediatype)
        base_dbc.mediatype = self.mediatype
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.tmdb_type = self.tmdb_type
        base_dbc.season = self.season
        base_dbc.episode = self.episode
        base_dbc.common_apis = self.common_apis
        base_dbc.connection = self.connection
        base_dbc.tmdb_id = self.tmdb_id
        return base_dbc.data

    def get_unmapped_data(self):
        with self.connection.open(self.cache):
            data = self.get_cached_list_values(
                self.cached_data_table,
                self.cached_data_keys,
                self.cached_data_values,
                self.cached_data_conditions
            )
        try:
            data_check = data[0][self.cached_data_check_key]
        except(TypeError, KeyError, AttributeError, IndexError):
            return
        if not data_check:
            return
        return data

    @staticmethod
    def map_item(i):
        return {k: i[k] for k in i.keys() if i[k]}

    def get_cached_data(self):
        data = self.get_unmapped_data()
        if not data:
            return
        return [self.map_item(i) for i in data]

    def try_cached_data(self, return_data=False):
        self.db_baseitem_cache_get_parent_data()
        if not return_data:
            return
        return self.get_cached_data()

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.try_cached_data()
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        if self.cache_refresh == 'check':
            return self.get_cached_data() or self.try_cached_data()
        return self.get_cached_data() or self.try_cached_data(True)
