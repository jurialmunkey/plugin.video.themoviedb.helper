#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.api.mapping import _ItemMapper


def split_array(items, subkeys=(), **kwargs):
    if not items:
        return ()

    for subkey in subkeys:
        try:
            items = items[subkey]
        except (TypeError, KeyError):
            return ()

    if not isinstance(items, list):
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
        'castmember': (),
        'crewmember': (),
        'person': [],
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
            'credits': [{
                'keys': [('castmember', None)],
                'func': split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'tmdb_id': 'id', 'role': 'character', 'ordering': 'order'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}}, {
                # ---
                'keys': [('crewmember', None)],
                'func': split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'tmdb_id': 'id', 'role': 'job', 'department': 'department', 'ordering': 'order'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}
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
