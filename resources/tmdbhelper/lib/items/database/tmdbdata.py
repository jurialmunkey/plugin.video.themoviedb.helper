#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.items.database.database import ItemDetailsDataBaseCache
from tmdbhelper.lib.api.mapping import _ItemMapper


def split_array(items, **kwargs):
    if not items or not isinstance(items, list):
        return ()

    def get_item(i, v):
        if not callable(v):
            return i.get(v)
        return v(i)

    return [{k: get_item(i, v) for k, v in kwargs.items()} for i in items]


def get_providers(items, **kwargs):
    if not items:
        return
    results = items.get('results')
    if not results:
        return
    data = []
    for iso, availabilities in results.items():
        for availability, datalist in availabilities.items():
            if availability == 'link':
                continue
            for provider in datalist:
                data.append({
                    'iso': iso,
                    'availability': availability,
                    'display_priority': provider.get('display_priority'),
                    'name': provider.get('provider_name'),
                    'logo': provider.get('logo_path'),
                    'tmdb_id': provider.get('provider_id'),
                })
    return data


class BlankNoneDict(dict):
    def __missing__(self, key):
        return None


def get_empty_item():
    return {
        'item': BlankNoneDict(),
        'genre': (),
        'country': (),
        'studio': (),
        'network': (),
        'provider': (),
    }


class ItemMapper(_ItemMapper):
    def __init__(self):
        self.blacklist = ()
        """ Mapping dictionary
        keys:       list of tuples containing parent and child key to add value. [('parent', 'child')]
                    parent keys: art, unique_ids, infolabels, infoproperties, params
                    use UPDATE_BASEKEY for child key to update parent with a dict
        func:       function to call to manipulate values (omit to skip and pass value directly)
        (kw)args:   list/dict of args/kwargs to pass to func.
                    func is also always passed v as first argument
        type:       int, float, str - convert v to type using try_type(v, type)
        extend:     set True to add to existing list - leave blank to overwrite exiting list
        subkeys:    list of sub keys to get for v - i.e. v.get(subkeys[0], {}).get(subkeys[1]) etc.
                    note that getting subkeys sticks for entire loop so do other ops on base first if needed

        use standard_map for direct one-to-one mapping of v onto single property tuple
        """
        self.advanced_map = {
            'release_date': [{
                'keys': [('item', 'premiered')]}, {
                'keys': [('item', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'genres': [{
                'keys': [('genre', None)],
                'func': split_array,
                'kwargs': {'name': 'name', 'tmdb_id': 'id'}
            }],
            'production_countries': [{
                'keys': [('country', None)],
                'func': split_array,
                'kwargs': {'name': 'name', 'iso': 'iso_3166_1'}
            }],
            'production_companies': [{
                'keys': [('studio', None)],
                'func': split_array,
                'kwargs': {'name': 'name', 'tmdb_id': 'id', 'icon': 'logo_path', 'country': 'origin_country'}
            }],
            'networks': [{
                'keys': [('network', None)],
                'func': split_array,
                'kwargs': {'name': 'name', 'tmdb_id': 'id', 'icon': 'logo_path', 'country': 'origin_country'}
            }],
            'watch/providers': [{
                'keys': [('provider', None)],
                'func': get_providers,
            }],

        }
        self.standard_map = {
            'id': ('item', 'tmdb_id'),
            'title': ('item', 'title'),
            'name': ('item', 'title'),
            'tagline': ('item', 'tagline'),
            'overview': ('item', 'plot'),
            'original_title': ('item', 'originaltitle'),
            'original_name': ('item', 'originaltitle'),
            'status': ('item', 'status'),
            'season_number': ('item', 'season'),
            'episode_number': ('item', 'episode'),
        }

    def get_info(self, data, **kwargs):
        item = get_empty_item()
        item = self.map_item(item, data)
        return item


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

    def configure_mapped_data(self, data):
        return {self.item_id: [data[self.item_info][k] for k in self.keys]}

    def configure_mapped_data_list(self, data):
        return {self.get_item_uid(i): [self.item_id if k == 'parent_id' else i[k] for k in self.keys] for i in data[self.table]}


class ListDetailsDataBaseCache(DetailsDataBaseCache):
    conditions = 'parent_id=?'  # WHERE conditions

    def get_cached_data(self):
        return self.cache.get_list_values(self.conditions, self.values, self.keys, self.table)

    def configure_mapped_data_list(self, data):
        return [tuple([self.item_id if k == 'parent_id' else i[k] for k in self.keys]) for i in data[self.table]]

    def set_cached_data(self, online_data_mapped):
        data = self.configure_mapped_data_list(online_data_mapped)
        self.cache.set_list_values(values=data, keys=self.keys, table=self.table)
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


class TMDbItemDetailsDataBaseCache(DetailsDataBaseCache):
    data_cond = True  # Condition to retrieve any data
    cache_refresh = None  # Set to "never" for cache only, or "force" for forced refresh
    item_info = 'item'

    @cached_property
    def keys(self):
        return [k for k in getattr(self.cache, f'{self.table}_columns').keys() if not k.startswith(('FOREIGN KEY', 'UNIQUE',))]

    @cached_property
    def table(self):
        return self.mediatype

    @cached_property
    def tmdb_type(self):
        if self.mediatype == 'movie':
            return 'movie'
        if self.mediatype in ('tvshow', 'season', 'episode', ):
            return 'tv'
        raise Exception(f'Invalid mediatype: {self.mediatype}')

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

    def get_db_cache(self, database_class):
        dbc = database_class()
        dbc.cache = self.cache
        dbc.mediatype = self.mediatype
        dbc.item_id = self.item_id
        return dbc

    @cached_property
    def db_studio_table(self):
        if self.mediatype == 'movie':
            return 'studio'
        return 'network'

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
    def db_provider_cache(self):
        return self.get_db_cache(ProviderDetailsDataBaseCache)

    def get_cached_data(self):
        # SELECT
        # Do some weird group concats since json array doesnt appear to be supported
        # Resplit list groups into infolabel lists as e.g. Action||Adventure -- genre: [Action, Adventure]
        # Resplit property_list into infoproperties as e.g. name=Australia|iso=AU||name=Germany|iso=DE -- country.1.name: Australia, country.1.iso: AU
        keys = (
            *[f'{self.table}.{k}' for k in self.keys],
            'replace(GROUP_CONCAT(DISTINCT genre.name), ",", "||") as list_genre',
            'replace(GROUP_CONCAT(DISTINCT country.name), ",", "||") as list_country',
            f'replace(GROUP_CONCAT(DISTINCT {self.db_studio_table}.name), ",", "||") as list_studio',  # Switch out studios for networks for TV Shows
            # 'replace(GROUP_CONCAT(DISTINCT "name=" || genre.name || "|tmdb_id=" || genre.tmdb_id), ",", "||") as property_list_genre',
            # 'replace(GROUP_CONCAT(DISTINCT "name=" || country.name || "|iso="  || country.iso), ",", "||") as property_list_country',
        )

        # FROM
        table = ' '.join((
            'baseitem',
            f'LEFT JOIN {self.table} ON {self.table}.id = baseitem.id',
            f'LEFT JOIN genre ON genre.parent_id = baseitem.id',
            f'LEFT JOIN country ON country.parent_id = baseitem.id',
            f'LEFT JOIN {self.db_studio_table} ON {self.db_studio_table}.parent_id = baseitem.id',
            f'LEFT JOIN provider ON provider.parent_id = baseitem.id',
        ))

        # WHERE
        conditions = f'{self.table}.id=?'

        # WHERE condition ? ? ? ? = value, value, value, value
        values = (self.item_id, )

        data = self.cache.get_list_values(conditions, values, keys, table)
        if not data[0]['tmdb_id']:
            return
        return data

    def set_cached_data(self):
        if not self.online_data_mapped:
            return
        self.cache.set_values(self.item_id, key_value_pairs=(('mediatype', self.mediatype), ('expiry', 'expiry'),), table='baseitem')
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
        self.db_genre_cache.set_cached_data(self.online_data_mapped)
        self.db_country_cache.set_cached_data(self.online_data_mapped)
        self.db_studio_cache.set_cached_data(self.online_data_mapped)
        self.db_provider_cache.set_cached_data(self.online_data_mapped)
        return self.get_cached_data()

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        if self.cache_refresh == 'force':
            return self.set_cached_data()
        if self.cache_refresh == 'never':
            return self.get_cached_data()
        return self.get_cached_data() or self.set_cached_data()
