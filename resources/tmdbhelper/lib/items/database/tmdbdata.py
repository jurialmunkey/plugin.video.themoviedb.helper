#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.items.database.database import ItemDetailsDataBase
from tmdbhelper.lib.items.database.mappings import ItemMapper
from tmdbhelper.lib.files.database import DataBaseCache
from tmdbhelper.lib.files.locker import mutexlock
# from tmdbhelper.lib.addon.logger import textviewer_output
# from tmdbhelper.lib.addon.logger import timer_report


class ItemDetailsDataBaseCache(DataBaseCache):
    cache_filename = 'ItemDetails.db'

    table = None  # Table in database
    conditions = 'id=?'  # WHERE conditions
    values = ()  # WHERE conditions values for ?
    keys = ()  # Keys to lookup
    online_data_func = None  # The function to get data e.g. get_response_json
    online_data_args = ()  # ARGS for online_data_func
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    item_sub_id_key = 'tmdb_id'

    @cached_property
    def cache(self):
        return ItemDetailsDataBase(filename=self.cache_filename)

    @cached_property
    def window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

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

    def get_item_uid(self, i):
        return f'{self.item_id}.{self.table}.{i[self.item_sub_id_key]}'

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

    def get_configure_mapped_data_list(self, i, k):
        if k == 'parent_id':
            return self.item_id
        return i.get(k)

    def configure_mapped_data(self, data):
        return {self.item_id: [self.get_configure_mapped_data(data, k) for k in self.keys]}

    def configure_mapped_data_list(self, data):
        return {self.get_item_uid(i): [self.get_configure_mapped_data_list(i, k) for k in self.keys] for i in data[self.table]}


class ItemDetailsListDataBaseCache(ItemDetailsDataBaseCache):
    conditions = 'parent_id=?'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.parent_id, )

    def get_cached_data(self):
        return self.get_cached_list_values(self.table, self.keys, self.values, self.conditions)

    def configure_mapped_data_list(self, data):
        return [tuple([self.get_configure_mapped_data_list(i, k) for k in self.keys]) for i in data[self.table]]

    def set_cached_data(self, online_data_mapped, return_data=False):
        self.set_cached_list_values(self.table, self.keys, self.configure_mapped_data_list(online_data_mapped))
        if not return_data:
            return
        return self.get_cached_data()


class StudioDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'studio'
    keys = ('name', 'tmdb_id', 'icon', 'country', 'parent_id', )


class CountryDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'country'
    keys = ('name', 'iso', 'parent_id', )
    item_sub_id_key = 'iso'


class GenreDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'genre'
    keys = ('name', 'tmdb_id', 'parent_id', )


class ProviderDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'provider'
    keys = ('name', 'tmdb_id', 'display_priority', 'iso', 'logo', 'availability', 'parent_id')

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class CastMemberDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'castmember'
    keys = ('tmdb_id', 'role', 'ordering', 'parent_id')


class CrewMemberDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'crewmember'
    keys = ('tmdb_id', 'role', 'department', 'ordering', 'parent_id')


class PersonDetailsDataBaseCache(ItemDetailsListDataBaseCache):
    table = 'person'
    keys = ('tmdb_id', 'thumb', 'name', 'gender', 'biography', 'known_for_department')
    conditions = 'tmdb_id=?'


class BaseItemDetailsDataBaseCache(ItemDetailsDataBaseCache):
    data_cond = True  # Condition to retrieve any data
    cache_refresh = None  # Set to "never" for cache only, or "force" for forced refresh
    item_info = 'item'
    expiry_time = 30 * 86400  # 30d = 86400 = 60s(1m) * 60m(1h) * 24h(1d)
    db_studio_table = 'studio'
    cached_data_check_key = 'tmdb_id'

    @property
    def expiry(self):
        return self.current_time + self.expiry_time

    @property
    def current_time(self):
        return set_timestamp(0, set_int=True)

    @cached_property
    def keys(self):
        return [k for k in getattr(self.cache, f'{self.table}_columns').keys()]

    @property
    def item_id(self):
        return self.parent_id

    @property
    def parent_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @cached_property
    def item_mapper(self):
        return ItemMapper()

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    def get_db_cache(self, database_class):
        dbc = database_class()
        dbc.cache = self.cache
        dbc.mediatype = self.mediatype
        dbc.item_id = self.item_id
        dbc.parent_id = self.parent_id
        dbc.connection = self.connection
        return dbc

    @cached_property
    def db_genre_cache(self):
        return self.get_db_cache(GenreDetailsDataBaseCache)

    @cached_property
    def db_country_cache(self):
        return self.get_db_cache(CountryDetailsDataBaseCache)

    @cached_property
    def db_studio_cache(self):
        dbc = self.get_db_cache(StudioDetailsDataBaseCache)
        dbc.table = self.db_studio_table  # Use networks not studios for TV
        return dbc

    @cached_property
    def db_castmember_cache(self):
        return self.get_db_cache(CastMemberDetailsDataBaseCache)

    @cached_property
    def db_crewmember_cache(self):
        return self.get_db_cache(CrewMemberDetailsDataBaseCache)

    @cached_property
    def db_person_cache(self):
        return self.get_db_cache(PersonDetailsDataBaseCache)

    @cached_property
    def db_provider_cache(self):
        return self.get_db_cache(ProviderDetailsDataBaseCache)

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.{self.item_id}.lockfile'

    @property
    def online_data_func(self):  # The function to get data e.g. get_response_json
        return self.tmdb_api.get_request_sc

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, )

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.tmdb_api.append_to_response}

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
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id'
        ))

    @property
    def cached_data_conditions(self):
        """ WHERE """
        return f'baseitem.id=? AND baseitem.expiry>=?'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, self.current_time, )

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        self.set_cached_values(table='baseitem', item_id=self.item_id, keys=('mediatype', 'expiry'), values=(self.mediatype, self.expiry))
        self.set_cached_many(self.table, self.keys, self.configure_mapped_data(self.online_data_mapped))
        self.db_genre_cache.set_cached_data(self.online_data_mapped)
        self.db_country_cache.set_cached_data(self.online_data_mapped)
        self.db_studio_cache.set_cached_data(self.online_data_mapped)
        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        self.db_person_cache.set_cached_data(self.online_data_mapped)
        self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        if not return_data:
            return

        return self.get_cached_data()

    def get_cached_data(self):
        data = self.get_cached_list_values(self.cached_data_table, self.cached_data_keys, self.cached_data_values, self.cached_data_conditions)
        if not data or not data[0] or not data[0][self.cached_data_check_key]:
            return

        item = {k: data[0][k] for k in data[0].keys() if k not in ('id', 'tmdb_id', )}

        routes = (
            (self.db_genre_cache, 'name', 'genre'),
            (self.db_country_cache, 'name', 'country'),
            (self.db_studio_cache, 'name', 'studio'),
        )

        for instance, name, key in routes:
            item[key] = [i[name] for i in instance.get_cached_data()]

        # {k: i[k] for i in sync.data for k in i.keys()}

        # self.db_genre_cache.set_cached_data(self.online_data_mapped)
        # self.db_country_cache.set_cached_data(self.online_data_mapped)
        # self.db_studio_cache.set_cached_data(self.online_data_mapped)
        # self.db_provider_cache.set_cached_data(self.online_data_mapped)
        # self.db_person_cache.set_cached_data(self.online_data_mapped)
        # self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        # self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        return item

    @mutexlock  # Use a mutex lock on the item_id to avoid double up of setting data or attempting get in middle of set
    def use_cached_data(self):
        return self.get_cached_data() or self.set_cached_data(return_data=True)

    @cached_property
    def data(self):
        return self.get_data()

    # @timer_report
    def get_data(self):
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.set_cached_data(return_data=True)
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        return self.use_cached_data()


class MovieItemDetailsDataBaseCache(BaseItemDetailsDataBaseCache):
    table = 'movie'
    tmdb_type = 'movie'


class TVShowItemDetailsDataBaseCache(BaseItemDetailsDataBaseCache):
    table = 'tvshow'
    tmdb_type = 'tv'
    db_studio_table = 'network'


class SeasonItemDetailsDataBaseCache(TVShowItemDetailsDataBaseCache):
    table = 'season'
    cached_data_check_key = 'tvshow_id'

    @property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def tvshow_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season)

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN tvshow ON tvshow.id = season.tvshow_id'
        ))

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        # Check we have base tvshow before mapping other data
        base_dbc = TVShowItemDetailsDataBaseCache()
        base_dbc.connection = self.connection
        base_dbc.mediatype = 'tvshow'
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.data

        self.set_cached_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.table, self.keys, self.configure_mapped_data(self.online_data_mapped))

        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        self.db_person_cache.set_cached_data(self.online_data_mapped)
        self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        if not return_data:
            return

        return self.get_cached_data()


class EpisodeItemDetailsDataBaseCache(SeasonItemDetailsDataBaseCache):
    table = 'episode'

    @property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    @property
    def season_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season, 'episode', self.episode)

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN season ON season.id = episode.season_id',
            f'LEFT JOIN tvshow ON tvshow.id = episode.tvshow_id',
        ))

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        # Check we have base season before mapping other data
        base_dbc = SeasonItemDetailsDataBaseCache()
        base_dbc.connection = self.connection
        base_dbc.mediatype = 'season'
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.season = self.season
        base_dbc.data

        self.set_cached_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.table, self.keys, self.configure_mapped_data(self.online_data_mapped))
        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        self.db_person_cache.set_cached_data(self.online_data_mapped)
        self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        if not return_data:
            return

        return self.get_cached_data()


def ItemDetailsDataBaseCacheFactory(mediatype, *args, **kwargs):

    routes = {
        'movie': MovieItemDetailsDataBaseCache,
        'tvshow': TVShowItemDetailsDataBaseCache,
        'season': SeasonItemDetailsDataBaseCache,
        'episode': EpisodeItemDetailsDataBaseCache,
    }

    dbc = routes[mediatype](*args, **kwargs)
    dbc.mediatype = mediatype
    return dbc
