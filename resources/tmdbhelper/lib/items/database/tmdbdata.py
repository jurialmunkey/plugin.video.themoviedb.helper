#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.items.database.database import ItemDetailsDataBaseCache
from tmdbhelper.lib.api.mapping import _ItemMapper


def split_array(items, dictionary=None, **kwargs):
    if not items or not isinstance(items, list):
        return ()
    return [{k: i.get(v) for k, v in kwargs.items()} for i in items]


class BlankNoneDict(dict):
    def __missing__(self, key):
        return None


def get_empty_item():
    return {
        'simplecache': BlankNoneDict(),
        'genre': (),
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
                'keys': [('simplecache', 'premiered')]}, {
                'keys': [('simplecache', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'genres': [{
                'keys': [('genre', None)],
                'func': split_array,
                'kwargs': {'name': 'name', 'tmdb_id': 'id'}
            }],
        }
        self.standard_map = {
            'id': ('simplecache', 'tmdb_id'),
            'title': ('simplecache', 'title'),
            'tagline': ('simplecache', 'tagline'),
            'overview': ('simplecache', 'plot'),
            'original_title': ('simplecache', 'originaltitle'),
            'original_name': ('simplecache', 'originaltitle'),
            'status': ('simplecache', 'status'),
            'season_number': ('simplecache', 'season'),
            'episode_number': ('simplecache', 'episode'),
        }

    def get_info(self, data, **kwargs):
        item = get_empty_item()
        item = self.map_item(item, data)
        return item


class DetailsDataBaseCache(ItemDetailsDataBaseCache):
    conditions = 'id=?'  # WHERE conditions
    table = ''
    keys = ()

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )

    def configure_mapped_data(self, data):
        return {self.item_id: [data[self.table][k] for k in self.keys]}

    def configure_mapped_data_list(self, data):
        return {self.get_item_uid(i): [self.item_id if k == 'parent_id' else i[k] for k in self.keys] for i in data[self.table]}


class GenreDetailsDataBaseCache(DetailsDataBaseCache):
    conditions = 'parent_id=?'  # WHERE conditions
    table = 'genre'
    keys = ('name', 'tmdb_id', )

    def get_item_uid(self, i):
        return f'{self.item_id}.genre.{i["tmdb_id"]}'

    def get_cached_data(self):
        return self.cache.get_list_values(self.conditions, self.values, self.keys, self.table)

    def set_cached_data(self, online_data_mapped):
        data = self.configure_mapped_data_list(online_data_mapped)
        self.set_cached_many(self.keys, self.table, data)
        return self.get_cached_data()


class TMDbItemDetailsDataBaseCache(DetailsDataBaseCache):
    table = 'simplecache'  # Table in database
    keys = (
        'mediatype', 'tmdb_id', 'season', 'episode', 'year', 'mpaa', 'plot', 'title',
        'originaltitle', 'duration', 'tagline', 'tvshowtitle', 'status', 'premiered', 'collection', 'trailer',
    )  # Keys to lookup
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    @cached_property
    def tmdb_type(self):
        if self.mediatype == 'movie':
            return 'movie'
        if self.mediatype in ('tvshow', 'season', 'episode', ):
            return 'tv'

    @property
    def item_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @cached_property
    def item_mapper(self):
        return ItemMapper()

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDbAPI
        return TMDbAPI()

    @property
    def online_data_func(self):  # The function to get data e.g. get_response_json
        return self.tmdb_api.get_request_sc

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, )

    @cached_property
    def online_data_mapped(self):
        """ function called when local cache does not have any data """
        if not self.online_data:
            return
        data = self.item_mapper.get_info(self.online_data)
        data['simplecache']['mediatype'] = self.mediatype
        return data

    def get_db_cache(self, database_class):
        dbc = database_class()
        dbc.cache = self.cache
        dbc.mediatype = self.mediatype
        dbc.item_id = self.item_id
        return dbc

    @cached_property
    def db_genre_cache(self):
        return self.get_db_cache(GenreDetailsDataBaseCache)

    def get_cached_data(self):
        # SELECT
        keys = (
            *[f'{self.table}.{k}' for k in self.keys],
            'GROUP_CONCAT(genre.name," / ") as genre',
            'GROUP_CONCAT(genre.name || "=" || genre.tmdb_id,"&") as properties_genre',
        )

        # FROM
        table = ' '.join((
            self.table,
            f'{self.table} LEFT JOIN genre ON genre.parent_id = {self.table}.id',
        ))

        # WHERE
        conditions = f'{self.table}.id=?'

        return self.cache.get_list_values(conditions, self.values, keys, table)

    def set_cached_data(self):
        if not self.online_data_mapped:
            return
        self.set_cached_many(self.keys, self.table, self.configure_mapped_data(self.online_data_mapped))
        self.db_genre_cache.set_cached_data(self.online_data_mapped)
        return self.get_cached_data()

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        return self.get_cached_data() or self.set_cached_data()
