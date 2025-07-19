from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.dbfunc import DatabaseAccess
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.api.contains import CommonContainerAPIs


class ItemDetailsDatabaseAccess(DatabaseAccess):
    # cache_filename = 'ItemDetails.db'

    table = None  # Table in database
    conditions = 'id=?'  # WHERE conditions
    values = ()  # WHERE conditions values for ?
    online_data_func = None  # The function to get data e.g. get_response_json
    online_data_args = ()  # ARGS for online_data_func
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    def __init__(self, common_apis=None):
        self.common_apis = common_apis or CommonContainerAPIs()

    @cached_property
    def cache(self):
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        return ItemDetailsDatabase()

    @cached_property
    def window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

    @property
    def expiry(self):
        return self.current_time + self.expiry_time

    @property
    def current_time(self):
        return set_timestamp(0, set_int=True)

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return tuple(getattr(self.cache, f'{self.table}_columns').keys())

    @staticmethod
    def get_base_id(tmdb_type, tmdb_id):
        return f'{tmdb_type}.{tmdb_id}'

    @staticmethod
    def get_season_id(tmdb_type, tmdb_id, season):
        return f'{tmdb_type}.{tmdb_id}.{season}'

    @staticmethod
    def get_episode_id(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    @property
    def online_data_cond(self):
        """ condition to determine whether to retrieve online data - defaults to data_cond """
        return self.data_cond

    @cached_property
    def online_data(self):
        """ cache online data from func to property """
        if not self.online_data_cond:
            return
        return self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

    def get_online_data(self):
        """ function called when local cache does not have any data """
        return self.online_data

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        return self.use_cached_many(
            self.table, self.keys, self.values, self.conditions,
            self.get_online_data
        )

    @property
    def item_info(self):
        return self.table

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )

    def get_configure_mapped_data(self, data, k):
        if k == 'tvshow_id':
            return self.tvshow_id
        if k == 'season_id':
            return self.season_id
        return data[self.item_info][k]

    def configure_mapped_data(self, data):
        return {self.item_id: [self.get_configure_mapped_data(data, k) for k in self.keys]}
