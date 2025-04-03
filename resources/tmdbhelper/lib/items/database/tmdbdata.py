#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.items.database.database import ItemDetailsDataBaseCache
from tmdbhelper.lib.api.mapping import _ItemMapper


class BlankNoneDict(dict):
    def __missing__(self, key):
        return None


def get_empty_item():
    return {
        'simplecache': BlankNoneDict()
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


class TMDbItemDetailsDataBaseCache(ItemDetailsDataBaseCache):
    table = 'simplecache'  # Table in database
    conditions = 'id=?'  # WHERE conditions
    keys = (
        'mediatype', 'tmdb_id', 'season', 'episode', 'year', 'mpaa', 'plot', 'title',
        'originaltitle', 'duration', 'tagline', 'tvshowtitle', 'status', 'premiered', 'collection', 'trailer',
    )  # Keys to lookup
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDbAPI
        return TMDbAPI()

    @cached_property
    def item_mapper(self):
        return ItemMapper()

    @cached_property
    def tmdb_type(self):
        if self.mediatype == 'movie':
            return 'movie'
        if self.mediatype in ('tvshow', 'season', 'episode', ):
            return 'tv'

    @property
    def online_data_func(self):  # The function to get data e.g. get_response_json
        return self.tmdb_api.get_request_sc

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, )

    @property
    def item_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )

    def get_online_data(self):
        """ function called when local cache does not have any data """
        if not self.online_data:
            return
        data = self.item_mapper.get_info(self.online_data)
        data['simplecache']['mediatype'] = self.mediatype
        return {self.item_id: [data[self.table][k] for k in self.keys]}
