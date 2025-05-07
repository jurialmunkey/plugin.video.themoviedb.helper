import contextlib
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.mappings import ItemMapper
from tmdbhelper.lib.items.database.basedata import ItemDetailsDatabaseAccess
from tmdbhelper.lib.items.database.basemeta_factories.factory import BaseMetaFactory
from tmdbhelper.lib.items.database.itemmeta_factories.factory import ItemMetaFactory
from infotagger.listitem import _ListItemInfoTagVideo
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_days_to_air
from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY, SHORTER_EXPIRY, DAY_IN_SECONDS


class BaseItem(ItemDetailsDatabaseAccess):
    cache_refresh = None  # Set to "never" for cache only, or "force" for forced refresh
    item_info = 'item'
    expiry_time = DEFAULT_EXPIRY
    cached_data_check_key = 'tmdb_id'
    extendedinfo = False
    routes_basemeta_db = {}
    allowlist_infolabel_keys = _ListItemInfoTagVideo._tag_attr

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        return not not self.tmdb_id

    @property
    def item_id(self):
        return self.parent_id

    @property
    def parent_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @cached_property
    def item_mapper(self):
        item_mapper = ItemMapper()
        item_mapper.tmdb_id = self.tmdb_id
        return item_mapper

    @property
    def has_fanart_tv(self):
        if not self.common_apis.ftv_api:
            return False
        if not self.ftv_id:
            return False
        return True

    @property
    def online_data_func(self):  # The function to get data e.g. get_response_json
        return self.common_apis.tmdb_api.get_response_json

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, )

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response}

    @cached_property
    def online_data_mapped(self):
        """ function called when local cache does not have any data """
        if not self.online_data:
            return
        data = self.item_mapper.get_info(self.online_data)
        data['item']['mediatype'] = self.mediatype
        return data

    @property
    def cached_data_keys(self):
        """ SELECT """
        return tuple([f'{self.table}.{k}' for k in self.keys])

    @property
    def cached_data_table(self):
        """ FROM """
        return f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id'

    @property
    def cached_data_conditions(self):
        """ WHERE """
        return 'baseitem.id=? AND baseitem.expiry>=?'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        if self.cache_refresh == 'never':
            return (self.item_id, 0, )
        return (self.item_id, self.current_time, )

    def db_baseitem_cache_get_parent_data(self):
        return

    @property
    def db_table_caches(self):
        return ()

    def config_basemeta_db(self, database_obj):
        database_obj.cache = self.cache
        database_obj.mediatype = self.mediatype
        database_obj.tmdb_id = self.tmdb_id
        database_obj.item_id = self.item_id
        database_obj.parent_id = self.parent_id
        database_obj.common_apis = self.common_apis
        database_obj.connection = self.connection
        return database_obj

    def return_basemeta_db(self, route, subtype=None):
        attr = f'basemeta_db_{route}' if not subtype else f'basemeta_db_{route}_{subtype}'

        with contextlib.suppress(AttributeError):
            return getattr(self, attr)

        if route.startswith('fanart_tv') and not self.has_fanart_tv:
            return

        configurator = self.routes_basemeta_db.get(attr) or self.config_basemeta_db
        database_obj = configurator(BaseMetaFactory(route))

        setattr(self, attr, database_obj)
        return database_obj

    def get_item_meta(self, data):
        """ configurator class to transform db cache data into a format usable for Kodi ListItem """
        imc = ItemMetaFactory(self, data)
        imc.extendedinfo = self.extendedinfo
        return imc.item

    def unaired_expiry(self, premiered=None, next_episode_to_air_id=None):
        if not premiered:
            self.expiry_time = SHORTER_EXPIRY
            return
        premiered = convert_timestamp(premiered, time_fmt="%Y-%m-%d", time_lim=10, utc_convert=False)
        if not premiered:
            self.expiry_time = SHORTER_EXPIRY
            return
        days_to_air, is_aired = get_days_to_air(premiered)
        if is_aired or not days_to_air:
            if next_episode_to_air_id:
                self.expiry_time = SHORTER_EXPIRY
            return
        self.expiry_time = ((days_to_air // 2) + 1) * DAY_IN_SECONDS  # Refresh in half number of days (rounded + 1)

    def get_cached_data(self):
        with self.connection.open():
            data = self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, self.cached_data_values, self.cached_data_conditions)
            if not data or not data[0] or not data[0][self.cached_data_check_key]:
                return
            return self.get_item_meta(data)

    def set_cached_data(self, item_id, mediatype, expiry, table, keys, mapped_data, return_data=False):
        if not return_data:
            self.del_cached('baseitem', item_id)
        self.set_cached_values('baseitem', item_id, keys=('mediatype', 'expiry'), values=(mediatype, expiry))
        self.set_cached_many(table, keys, mapped_data)

    def try_cached_data(self, return_data=False):
        online_data_mapped = self.online_data_mapped
        if not online_data_mapped:
            return

        # Check for parent data (if needed)
        self.db_baseitem_cache_get_parent_data()

        # Check for future items to lower expiry and refresh more frequently closer to premiere
        self.unaired_expiry(online_data_mapped['item'].get('premiered'), online_data_mapped['item'].get('next_episode_to_air_id'))

        # TODO: A better queuing method
        func = self.set_cached_data
        args = (
            self.item_id, self.mediatype, self.expiry, self.table, self.keys,
            self.configure_mapped_data(online_data_mapped))
        kwgs = {'return_data': return_data}

        queue = []
        queue.append((func, args, kwgs))

        for db_cache in self.db_table_caches:
            with contextlib.suppress(AttributeError):
                qitem = db_cache.try_cached_data(online_data_mapped)
                queue.append(qitem)

        with self.connection.open():
            self.connection.open_connection.execute('BEGIN')
            for func, args, kwgs in queue:
                func(*args, **kwgs)
            self.connection.open_connection.execute('COMMIT')
        if not return_data:
            return
        return self.get_cached_data()

    @cached_property
    def data(self):
        """ cached_property wrapper to set get_data to attribute for reuse """
        return self.get_data()

    def get_data(self):
        """ Get data from the cache
        cache_refresh = 'force' to force data refresh
        cache_refresh = 'never' to never refresh from online and only get cached data
        cache_refresh = None to get data from cache if available and hasn't expired otherwise cache new data and return it
        """
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.try_cached_data()
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        if self.cache_refresh == 'check':
            return self.get_cached_data() or self.try_cached_data()
        return self.get_cached_data() or self.try_cached_data(True)
