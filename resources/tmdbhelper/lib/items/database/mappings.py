#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.api.mapping import _ItemMapper


class ItemMapperMethods:

    @staticmethod
    def get_runtime(v, *args, **kwargs):
        if isinstance(v, list):
            v = v[0]
        try:
            return int(v) * 60
        except (TypeError, ValueError):
            return 0

    @staticmethod
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

    @staticmethod
    def get_providers(items, service=False, **kwargs):
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
                    if service:
                        item = {
                            'iso_country': iso,
                            'display_priority': provider.get('display_priority'),
                            'name': provider.get('provider_name'),
                            'logo': provider.get('logo_path'),
                            'tmdb_id': provider.get('provider_id'),
                        }
                    else:
                        item = {
                            'availability': availability,
                            'tmdb_id': provider.get('provider_id'),
                        }
                    data.append(item)
        return data

    @staticmethod
    def get_certifications(items, **kwargs):
        if not items:
            return
        results = items.get('results')
        if not results:
            return
        data = []
        tmdb_release_types = {1: 'Premiere', 2: 'Limited', 3: 'Theatrical', 4: 'Digital', 5: 'Physical', 6: 'TV'}
        for release_country in results:
            iso_country = release_country['iso_3166_1']
            for release in (release_country.get('release_dates') or ()):
                data.append({
                    'name': release['certification'],
                    'iso_country': iso_country,
                    'iso_language': release['iso_639_1'],
                    'release_date': release['release_date'],
                    'release_type': tmdb_release_types.get(release['type']),
                })
        return data

    @staticmethod
    def get_video(items, **kwargs):
        if not items:
            return
        results = items.get('results')
        if not results:
            return
        data = []
        for video in results:
            if video['site'] != 'YouTube':
                continue
            data.append({
                'name': video['name'],
                'iso_country': video['iso_3166_1'],
                'iso_language': video['iso_639_1'],
                'release_date': video['published_at'],
                'content': video['type'],
                'path': f"plugin://plugin.video.youtube/play/?video_id={video['key']}",
            })
        return data

    @staticmethod
    def get_art(items, **kwargs):
        if not items:
            return
        data = []

        def get_aspect_ratio(aspect_ratio):
            if aspect_ratio < 1:
                return 'poster'
            if aspect_ratio == 1:
                return 'square'
            if 1.7 <= aspect_ratio <= 1.8:
                return 'landscape'
            if aspect_ratio < 1.7:
                return 'thumb'
            if aspect_ratio > 1.8:
                return 'wide'
            return 'other'

        for artwork_type, artworks in items.items():
            for artwork in artworks:
                path = artwork['file_path']
                data.append({
                    'aspect_ratio': get_aspect_ratio(artwork['aspect_ratio']),
                    'height': artwork['height'],
                    'width': artwork['width'],
                    'iso_language': artwork['iso_639_1'],
                    'icon': path,
                    'type': artwork_type,
                    'extension': path.split('.')[-1] if path else None,
                    'vote_average': int(artwork['vote_average'] * 100),
                    'vote_count': artwork['vote_count'],
                })

        return data

    @staticmethod
    def get_unique_ids(results, **kwargs):
        if not results:
            return
        return [{'key': ('tmdb_id' if k == 'id' else k).replace('_id', ''), 'value': f'{v}'} for k, v in results.items()]


class BlankNoneDict(dict):
    def __missing__(self, key):
        return None


class ItemMapper(_ItemMapper, ItemMapperMethods):
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
            'first_air_date': [{
                'keys': [('item', 'premiered')]}, {
                'keys': [('item', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'air_date': [{
                'keys': [('item', 'premiered')]}, {
                'keys': [('item', 'year')],
                'func': lambda v: int(v[0:4])
            }],
            'episode_run_time': [{
                'keys': [('item', 'duration')],
                'func': self.get_runtime
            }],
            'runtime': [{
                'keys': [('item', 'duration')],
                'func': self.get_runtime
            }],
            'genres': [{
                'keys': [('genre', None)],
                'func': self.split_array,
                'kwargs': {'name': 'name', 'tmdb_id': 'id'}
            }],
            'content_ratings': [{
                'keys': [('certification', None)],
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('results', ),
                    'name': 'rating', 'iso_country': 'iso_3166_1'}
            }],
            'release_dates': [{
                'keys': [('certification', None)],
                'func': self.get_certifications,
            }],
            'production_countries': [{
                'keys': [('country', None)],
                'func': self.split_array,
                'kwargs': {'name': 'name', 'iso_country': 'iso_3166_1'}
            }],
            'production_companies': [{
                'keys': [('studio', None)],
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id'}}, {
                # ---
                'keys': [('company', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id', 'name': 'name', 'logo': 'logo_path', 'country': 'origin_country'}
            }],
            'networks': [{
                'keys': [('network', None)],
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id'}}, {
                # ---
                'keys': [('company', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id', 'name': 'name', 'logo': 'logo_path', 'country': 'origin_country'}
            }],
            'watch/providers': [{
                'keys': [('provider', None)],
                'func': self.get_providers}, {
                # ---
                'keys': [('service', None)],
                'extend': True,
                'func': self.get_providers,
                'kwargs': {'service': True}
            }],
            'images': [{
                'keys': [('art', None)],
                'func': self.get_art,
            }],
            'external_ids': [{
                'keys': [('unique_id', None)],
                'func': self.get_unique_ids,
            }],
            'videos': [{
                'keys': [('video', None)],
                'func': self.get_video,
            }],
            'credits': [{
                'keys': [('castmember', None)],
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'tmdb_id': 'id', 'role': 'character', 'ordering': 'order'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}}, {
                # ---
                'keys': [('crewmember', None)],
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'tmdb_id': 'id', 'role': 'job', 'department': 'department'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
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
            'episode_type': ('item', 'status'),
        }

    @staticmethod
    def get_empty_item():
        return {
            'item': BlankNoneDict(),
            'genre': (),
            'country': (),
            'company': [],
            'studio': (),
            'network': (),
            'provider': (),
            'certification': (),
            'service': [],
            'video': (),
            'castmember': (),
            'crewmember': (),
            'unique_id': [],
            'person': [],
            'art': (),
        }

    def get_info(self, data, **kwargs):
        item = self.get_empty_item()
        item = self.map_item(item, data)
        return item
