#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.items.database.database import ItemDetailsDataBaseCache
from tmdbhelper.lib.items.database.mappings import ItemMapper
from tmdbhelper.lib.files.locker import mutexlock
# from tmdbhelper.lib.addon.logger import textviewer_output
from tmdbhelper.lib.items.listitem import ListItem


class DetailsDataBaseCache(ItemDetailsDataBaseCache):
    conditions = 'id=?'  # WHERE conditions
    table = ''
    keys = ()

    item_sub_id_key = 'tmdb_id'

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


class ListDetailsDataBaseCache(DetailsDataBaseCache):
    conditions = 'parent_id=?'  # WHERE conditions

    def get_cached_data(self):
        return self.cache.get_list_values(self.conditions, self.values, self.keys, self.table)

    def configure_mapped_data_list(self, data):
        return [tuple([self.get_configure_mapped_data_list(i, k) for k in self.keys]) for i in data[self.table]]

    def set_cached_data(self, online_data_mapped, return_data=False):
        data = self.configure_mapped_data_list(online_data_mapped)
        self.cache.set_list_values(values=data, keys=self.keys, table=self.table)
        if not return_data:
            return
        return self.get_cached_data()


class StudioDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'studio'
    keys = ('name', 'tmdb_id', 'icon', 'country', 'parent_id', )


class CountryDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'country'
    keys = ('name', 'iso', 'parent_id', )
    item_sub_id_key = 'iso'


class GenreDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'genre'
    keys = ('name', 'tmdb_id', 'parent_id', )


class ProviderDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'provider'
    keys = ('name', 'tmdb_id', 'display_priority', 'iso', 'logo', 'availability', 'parent_id')


class CastMemberDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'castmember'
    keys = ('tmdb_id', 'role', 'ordering', 'parent_id')


class CrewMemberDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'crewmember'
    keys = ('tmdb_id', 'role', 'department', 'ordering', 'parent_id')


class PersonDetailsDataBaseCache(ListDetailsDataBaseCache):
    table = 'person'
    keys = ('tmdb_id', 'thumb', 'name', 'gender', 'biography', 'known_for_department')
    conditions = 'tmdb_id=?'


class TMDbItemDetailsDataBaseCache(DetailsDataBaseCache):
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
        return [k for k in getattr(self.cache, f'{self.table}_columns').keys() if not k.startswith(('FOREIGN KEY', 'UNIQUE',))]

    @property
    def item_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @cached_property
    def item_mapper(self):
        return ItemMapper()

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

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
        return (*[f'{self.table}.{k}' for k in self.keys],)

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
        ))

    @property
    def cached_data_conditions(self):
        """ WHERE """
        return f'baseitem.id=? AND baseitem.expiry>=?'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, self.current_time, )

    def get_cached_data(self):
        data = self.cache.get_list_values(self.cached_data_conditions, self.cached_data_values, self.cached_data_keys, self.cached_data_table)
        if not data[0][self.cached_data_check_key]:
            return
        return data

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return
        self.cache.set_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
        if not return_data:
            return
        return self.get_cached_data()

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.{self.item_id}.lockfile'

    @mutexlock  # Use a mutex lock on the item_id to avoid double up of setting data or attempting get in middle of set
    def use_cached_data(self):
        return self.get_cached_data() or self.set_cached_data(return_data=True)

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.set_cached_data(return_data=True)
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        return self.use_cached_data()


class TMDbBaseItemDetailsDataBaseCache(TMDbItemDetailsDataBaseCache):
    def get_db_cache(self, database_class):
        dbc = database_class()
        dbc.cache = self.cache
        dbc.mediatype = self.mediatype
        dbc.item_id = self.item_id
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
    def cached_data_keys(self):
        """ SELECT """
        # Do some weird group concats since json array doesnt appear to be supported
        # Resplit list groups into infolabel lists as e.g. Action||Adventure -- genre: [Action, Adventure]
        # Resplit property_list into infoproperties as e.g. name=Australia|iso=AU||name=Germany|iso=DE -- country.1.name: Australia, country.1.iso: AU
        return (
            *[f'{self.table}.{k}' for k in self.keys],
            'replace(GROUP_CONCAT(DISTINCT genre.name), ",", "||") as list_genre',
            'replace(GROUP_CONCAT(DISTINCT country.name), ",", "||") as list_country',
            'replace(GROUP_CONCAT(DISTINCT provider.name), ",", "||") as list_provider',
            # 'replace(GROUP_CONCAT(DISTINCT castperson.name), ",", "||") as list_cast',
            # 'replace(GROUP_CONCAT(DISTINCT crewperson.name), ",", "||") as list_crew',

            f'replace(GROUP_CONCAT(DISTINCT {self.db_studio_table}.name), ",", "||") as list_studio',  # Switch out studios for networks for TV Shows
            # 'replace(GROUP_CONCAT(DISTINCT "name=" || genre.name || "|tmdb_id=" || genre.tmdb_id), ",", "||") as property_list_genre',
            # 'replace(GROUP_CONCAT(DISTINCT "name=" || country.name || "|iso="  || country.iso), ",", "||") as property_list_country',
        )

    @property
    def cached_data_table(self):
        """ FROM """
        return ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN genre ON genre.parent_id = baseitem.id',
            f'LEFT JOIN country ON country.parent_id = baseitem.id',
            f'LEFT JOIN {self.db_studio_table} ON {self.db_studio_table}.parent_id = baseitem.id',
            f'LEFT JOIN provider ON provider.parent_id = baseitem.id',
            # f'LEFT JOIN (castmember INNER JOIN person ON person.tmdb_id = castmember.tmdb_id) AS castperson ON castperson.parent_id = baseitem.id',
            # f'LEFT JOIN (crewmember INNER JOIN person ON person.tmdb_id = crewmember.tmdb_id) AS crewperson ON crewperson.parent_id = baseitem.id',
        ))

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        self.cache.set_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
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


class TMDbMovieItemDetailsDataBaseCache(TMDbBaseItemDetailsDataBaseCache):
    table = 'movie'
    tmdb_type = 'movie'


class TMDbTVShowItemDetailsDataBaseCache(TMDbBaseItemDetailsDataBaseCache):
    table = 'tvshow'
    tmdb_type = 'tv'
    db_studio_table = 'network'


class TMDbSeasonItemDetailsDataBaseCache(TMDbTVShowItemDetailsDataBaseCache):
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
            f'LEFT JOIN tvshow ON tvshow.id = season.tvshow_id',
            f'LEFT JOIN genre ON genre.parent_id = season.tvshow_id',
            f'LEFT JOIN country ON country.parent_id = season.tvshow_id',
            f'LEFT JOIN {self.db_studio_table} ON {self.db_studio_table}.parent_id = season.tvshow_id',
            f'LEFT JOIN provider ON provider.parent_id = baseitem.id',  # Seasons individually have providers
            # f'LEFT JOIN (castmember INNER JOIN person ON person.tmdb_id = castmember.tmdb_id) AS castperson ON castperson.parent_id = baseitem.id',
            # f'LEFT JOIN (crewmember INNER JOIN person ON person.tmdb_id = crewmember.tmdb_id) AS crewperson ON crewperson.parent_id = baseitem.id',
        ))

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        # Check we have base tvshow before mapping other data
        base_dbc = TMDbTVShowItemDetailsDataBaseCache()
        base_dbc.mediatype = 'tvshow'
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.data

        self.cache.set_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        self.db_person_cache.set_cached_data(self.online_data_mapped)
        self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        if not return_data:
            return

        return self.get_cached_data()


class TMDbEpisodeItemDetailsDataBaseCache(TMDbSeasonItemDetailsDataBaseCache):
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
            f'LEFT JOIN genre ON genre.parent_id = episode.tvshow_id',
            f'LEFT JOIN country ON country.parent_id = episode.tvshow_id',
            f'LEFT JOIN {self.db_studio_table} ON {self.db_studio_table}.parent_id = episode.tvshow_id',
            f'LEFT JOIN provider ON provider.parent_id = baseitem.id',  # Episodes individually have providers
            # f'LEFT JOIN (castmember INNER JOIN person ON person.tmdb_id = castmember.tmdb_id) AS castperson ON castperson.parent_id = baseitem.id',
            # f'LEFT JOIN (crewmember INNER JOIN person ON person.tmdb_id = crewmember.tmdb_id) AS crewperson ON crewperson.parent_id = baseitem.id',
        ))

    def set_cached_data(self, return_data=False):
        if not self.online_data_mapped:
            return

        # Check we have base season before mapping other data
        base_dbc = TMDbSeasonItemDetailsDataBaseCache()
        base_dbc.mediatype = 'season'
        base_dbc.tmdb_id = self.tmdb_id
        base_dbc.season = self.season
        base_dbc.data

        self.cache.set_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', self.expiry),), table='baseitem')
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        self.db_person_cache.set_cached_data(self.online_data_mapped)
        self.db_castmember_cache.set_cached_data(self.online_data_mapped)
        self.db_crewmember_cache.set_cached_data(self.online_data_mapped)

        if not return_data:
            return

        return self.get_cached_data()


def TMDbItemDetailsDataBaseCacheFactory(mediatype, *args, **kwargs):

    routes = {
        'movie': TMDbMovieItemDetailsDataBaseCache,
        'tvshow': TMDbTVShowItemDetailsDataBaseCache,
        'season': TMDbSeasonItemDetailsDataBaseCache,
        'episode': TMDbEpisodeItemDetailsDataBaseCache,
    }

    dbc = routes[mediatype](*args, **kwargs)
    dbc.mediatype = mediatype
    return dbc


def configure_listitem(i):
    li = ListItem(**i)
    mediatype = li.infolabels.get('mediatype')

    if mediatype not in ('movie', 'tvshow', 'season', 'episode'):
        return li

    dbc = TMDbItemDetailsDataBaseCacheFactory(mediatype)
    dbc.tmdb_id = li.unique_ids.get('tmdb')
    if mediatype in ['season', 'episode']:
        dbc.season = li.infolabels.get('season', 0)
        dbc.tmdb_id = li.unique_ids.get('tvshow.tmdb')
    if mediatype == 'episode':
        dbc.episode = li.infolabels.get('episode')

    if not dbc.data:
        return li

    item = {'infolabels': {k: i[k] for i in dbc.data for k in i.keys() if k in ('title', 'plot')}}

    li.set_details(item, override=True)

    # li.art = self.get_item_artwork(item['artwork'], is_season=mediatype in ['season', 'episode'])
    return li
