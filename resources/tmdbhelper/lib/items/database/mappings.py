#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.api.mapping import _ItemMapper


def get_blanks_none(i):
    """
    Convert empty strings to nulls
    """
    return i if i or i == 0 else None


class ItemMapperMethods:
    @staticmethod
    def get_runtime(v, *args, **kwargs):
        if isinstance(v, list):
            v = v[0]
        try:
            return int(v) * 60
        except (TypeError, ValueError):
            return 0

    def add_art_type(self, item_id, path, art_type, aspect_ratio):
        from tmdbhelper.lib.addon.consts import IMAGEPATH_ASPECTRATIO
        return {
            'parent_id': item_id,
            'aspect_ratio': IMAGEPATH_ASPECTRATIO.index(aspect_ratio),
            'quality': 0,
            'icon': get_blanks_none(path),
            'type': art_type,
            'extension': get_blanks_none(path.split('.')[-1] if path else None),
            'rating': 0,
            'votes': 0,
        }

    def add_season_episodes_art(self, v, **kwargs):
        art = []

        for i in v:
            if 'still_path' in i:
                art.append(self.add_art_type(
                    item_id=f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}',
                    path=i['still_path'],
                    art_type='stills',
                    aspect_ratio='landscape'))

        return art

    def add_seasons_art(self, v, **kwargs):
        art = []

        for i in v:
            if 'poster_path' in i:
                art.append(self.add_art_type(
                    item_id=f'tv.{self.tmdb_id}.{i["season_number"]}',
                    path=i['poster_path'],
                    art_type='posters',
                    aspect_ratio='poster'))

        return art

    @staticmethod
    def split_array(items, subkeys=(), haskeys=(), **kwargs):
        if not items:
            return []

        for subkey in subkeys:
            try:
                items = items[subkey]
            except (TypeError, KeyError):
                return []

        if not isinstance(items, list):
            return []

        def get_item(i, v):
            try:
                if not callable(v):
                    return i.get(v)
                return v(i)
            except (TypeError, KeyError, IndexError, ValueError):
                return

        def get_configured_item(i, v):
            return get_blanks_none(get_item(i, v))

        def check_item(i):
            for k in haskeys:
                try:
                    if not i[k]:
                        return
                except (TypeError, KeyError, IndexError, ValueError):
                    return
            return i

        items = [i for i in items if check_item(i)] if haskeys else items
        return [{k: get_configured_item(i, v) for k, v in kwargs.items()} for i in items]

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
                            'display_priority': get_blanks_none(provider.get('display_priority')),
                            'name': get_blanks_none(provider.get('provider_name')),
                            'logo': get_blanks_none(provider.get('logo_path')),
                            'tmdb_id': get_blanks_none(provider.get('provider_id')),
                        }
                    else:
                        item = {
                            'availability': get_blanks_none(availability),
                            'tmdb_id': get_blanks_none(provider.get('provider_id')),
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
                    'name': get_blanks_none(release['certification']),
                    'iso_country': get_blanks_none(iso_country),
                    'iso_language': get_blanks_none(release['iso_639_1']),
                    'release_date': get_blanks_none(release['release_date']),
                    'release_type': get_blanks_none(tmdb_release_types.get(release['type'])),
                })
        return data

    def get_fanart_tv(self, items, **kwargs):
        if not items:
            return

        art_types = {
            'movieposter': ('poster', False),
            'moviebackground': ('fanart', False),
            'moviethumb': ('landscape', False),
            'moviebanner': ('banner', False),
            'hdmovieclearart': ('clearart', False),
            'movieclearart': ('clearart', False),
            'hdmovielogo': ('clearlogo', False),
            'movielogo': ('clearlogo', False),
            'moviedisc': ('discart', False),
            'tvposter': ('poster', False),
            'tvthumb': ('landscape', False),
            'tvbanner': ('banner', False),
            'hdclearart': ('clearart', False),
            'clearart': ('clearart', False),
            'hdtvlogo': ('clearlogo', False),
            'clearlogo': ('clearlogo', False),
            'characterart': ('characterart', False),
            'showbackground': ('fanart', True),
            'seasonposter': ('poster', True),
            'seasonbanner': ('banner', True),
            'seasonthumb': ('landscape', True),
        }

        data = []
        for art_type, art_list in items.items():
            if not isinstance(art_list, list):
                continue
            quality = 1 if art_type.startswith('hd') else 0
            art_type = art_types.get(art_type)
            if not art_type:
                continue
            art_type, art_has_seasons = art_type
            for art_item in art_list:
                path = art_item['url']
                item = {
                    'icon': get_blanks_none(path),
                    'iso_language': get_blanks_none(art_item.get('lang')),
                    'likes': get_blanks_none(art_item.get('likes')),
                    'type': get_blanks_none(art_type),
                    'quality': get_blanks_none(quality),
                    'extension': get_blanks_none(path.split('.')[-1] if path else None),
                }

                if art_has_seasons:
                    snum = (art_item.get('season') or 'all')
                    if snum != 'all':
                        item['parent_id'] = f'tv.{self.tmdb_id}.{snum}'
                        self.item['baseitem'].append({
                            'id': f'tv.{self.tmdb_id}.{snum}',
                            'mediatype': 'season',
                            'expiry': 0,
                        })

                data.append(item)

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
                'name': get_blanks_none(video['name']),
                'iso_country': get_blanks_none(video['iso_3166_1']),
                'iso_language': get_blanks_none(video['iso_639_1']),
                'release_date': get_blanks_none(video['published_at']),
                'key': get_blanks_none(video['key']),
                'content': get_blanks_none(video['type']),
                'path': f"plugin://plugin.video.youtube/play/?video_id={video['key']}",
            })
        return data

    @staticmethod
    def get_aspect_ratio(aspect_ratio):
        from tmdbhelper.lib.addon.consts import IMAGEPATH_ASPECTRATIO
        if aspect_ratio < 1:
            return IMAGEPATH_ASPECTRATIO.index('poster')
        if aspect_ratio == 1:
            return IMAGEPATH_ASPECTRATIO.index('square')
        if 1.7 <= aspect_ratio <= 1.8:
            return IMAGEPATH_ASPECTRATIO.index('landscape')
        if aspect_ratio < 1.7:
            return IMAGEPATH_ASPECTRATIO.index('thumb')
        if aspect_ratio > 1.8:
            return IMAGEPATH_ASPECTRATIO.index('wide')
        return IMAGEPATH_ASPECTRATIO.index('other')

    @staticmethod
    def get_art(items, **kwargs):
        if not items:
            return
        data = []

        for artwork_type, artworks in items.items():
            for artwork in artworks:
                path = artwork['file_path']
                data.append({
                    'aspect_ratio': ItemMapperMethods.get_aspect_ratio(artwork['aspect_ratio']),
                    'quality': int((artwork['width'] * artwork['height']) // 200000),  # Quality integer to nearest fifth of a megapixel
                    'iso_language': get_blanks_none(artwork['iso_639_1']),
                    'icon': get_blanks_none(path),
                    'type': get_blanks_none(artwork_type),
                    'extension': get_blanks_none(path.split('.')[-1] if path else None),
                    'rating': int(artwork['vote_average'] * 100),
                    'votes': get_blanks_none(artwork['vote_count']),
                })

        return data

    @staticmethod
    def get_unique_ids(results, **kwargs):
        if not results:
            return
        return [
            {
                'key': get_blanks_none(('tmdb_id' if k == 'id' else k).replace('_id', '')),
                'value': get_blanks_none(f'{v}')
            }
            for k, v in results.items()
        ]

    @staticmethod
    def get_episode_to_air(v, name):
        from jurialmunkey.parser import try_float
        from tmdbhelper.lib.addon.tmdate import format_date_obj, convert_timestamp, get_days_to_air
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath

        i = v or {}
        air_date = i.get('air_date')
        air_date_obj = convert_timestamp(air_date, time_fmt="%Y-%m-%d", time_lim=10, utc_convert=False)
        infoproperties = {}
        infoproperties[f'{name}'] = format_date_obj(air_date_obj, region_fmt='dateshort')
        infoproperties[f'{name}_long'] = format_date_obj(air_date_obj, region_fmt='datelong')
        infoproperties[f'{name}_short'] = format_date_obj(air_date_obj, "%d %b")
        infoproperties[f'{name}_day'] = format_date_obj(air_date_obj, "%A")
        infoproperties[f'{name}_day_short'] = format_date_obj(air_date_obj, "%a")
        infoproperties[f'{name}_year'] = format_date_obj(air_date_obj, "%Y")
        infoproperties[f'{name}_episode'] = i.get('episode_number')
        infoproperties[f'{name}_name'] = i.get('name')
        infoproperties[f'{name}_tmdb_id'] = i.get('id')
        infoproperties[f'{name}_plot'] = i.get('overview')
        infoproperties[f'{name}_season'] = i.get('season_number')
        infoproperties[f'{name}_rating'] = f'{try_float(i.get("vote_average")):0,.1f}'
        infoproperties[f'{name}_votes'] = i.get('vote_count')
        infoproperties[f'{name}_thumb'] = TMDbImagePath().get_imagepath_thumbs(i.get('still_path'))
        infoproperties[f'{name}_original'] = air_date

        if air_date_obj:
            days_to_air, is_aired = get_days_to_air(air_date_obj)
            infoproperties[f'{name}_days_from_aired' if is_aired else f'{name}_days_until_aired'] = str(days_to_air)

        return infoproperties


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
            'name': [{
                'keys': [('item', 'title')]}, {
                'keys': [('item', 'name')],
            }],
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
            'belongs_to_collection': [{
                'keys': [('baseitem', None)],
                'extend': True,
                'func': lambda v: [{
                    'id': f"collection.{v['id']}",
                    'mediatype': 'collection',
                    'expiry': 0}]}, {
                # ---
                'keys': [('collection', None)],
                'extend': True,
                'func': lambda v: [{
                    'id': f"collection.{v['id']}",
                    'tmdb_id': v['id'],
                    'title': v['name'],
                    'poster': v.get('poster_path'),
                    'fanart': v.get('backdrop_path')}]}, {
                # ---
                'keys': [('item', 'collection_id')],
                'func': lambda v: f"collection.{v['id']}"
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
            'seasons': [{
                'keys': [('season', None)],
                'func': self.split_array,
                'extend': True,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}',
                    'tvshow_id': lambda i: f'tv.{self.tmdb_id}',
                    'season': 'season_number',
                    'year': lambda i: int(i['air_date'][0:4]),
                    'premiered': 'air_date',
                    'title': 'name',
                    'plot': 'overview',
                    'rating': 'vote_average'}}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}',
                    'mediatype': lambda _: 'season',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('art', None)],
                'extend': True,
                'func': self.add_seasons_art
            }],
            'episodes': [{
                'keys': [('episode', None)],
                'func': self.split_array,
                'extend': True,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}',
                    'season_id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}',
                    'tvshow_id': lambda i: f'tv.{self.tmdb_id}',
                    'episode': 'episode_number',
                    'year': lambda i: int(i['air_date'][0:4]),
                    'premiered': 'air_date',
                    'title': 'name',
                    'plot': 'overview',
                    'rating': 'vote_average',
                    'votes': 'vote_count',
                    'duration': 'runtime'}}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}',
                    'mediatype': lambda _: 'episode',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('art', None)],
                'extend': True,
                'func': self.add_season_episodes_art
            }],
            'next_episode_to_air': [{
                'keys': [('episode', None)],
                'func': self.split_array,
                'extend': True,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}',
                    'season_id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}',
                    'tvshow_id': lambda i: f'tv.{self.tmdb_id}',
                    'episode': 'episode_number',
                    'premiered': 'air_date',
                    'title': 'name',
                    'plot': 'overview',
                    'rating': 'vote_average',
                    'votes': 'vote_count',
                    'duration': 'runtime'}}, {
                # ---
                'keys': [('season', None)],
                'func': self.split_array,
                'extend': True,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}',
                    'tvshow_id': lambda i: f'tv.{self.tmdb_id}',
                    'season': 'season_number'}}, {
                # ---
                'keys': [('item', 'next_episode_to_air_id')],
                'func': lambda v: f'tv.{self.tmdb_id}.{v["season_number"]}'}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'id': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}',
                    'mediatype': lambda _: 'episode',
                    'expiry': lambda _: 0}
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
                'keys': [('broadcaster', None)],
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
                'extend': True,
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
            'created_by': [{
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('crewmember', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'tmdb_id': 'id',
                    'role': lambda _: 'Creator',
                    'department': lambda _: 'Creator'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender'}
            }],
            'credits': [{
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('castmember', None)],
                'extend': True,
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
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('crewmember', None)],
                'extend': True,
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
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('guest_stars', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('castmember', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('guest_stars', ),
                    'tmdb_id': 'id', 'role': 'character', 'ordering': 'order'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('guest_stars', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}
            }],
            'aggregate_credits': [{
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('castmember', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'tmdb_id': 'id',
                    'role': lambda i: ' / '.join([j['character'] for j in i['roles']]),
                    'ordering': 'order',
                    'appearances': 'total_episode_count'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('cast', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}}, {
                # ---
                'keys': [('baseitem', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'mediatype': lambda _: 'person',
                    'expiry': lambda _: 0}}, {
                # ---
                'keys': [('crewmember', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'tmdb_id': 'id',
                    'role': lambda i: ' / '.join([j['job'] for j in i['jobs']]),
                    'ordering': 'order',
                    'department': 'department',
                    'appearances': 'total_episode_count'}}, {
                # ---
                'keys': [('person', None)],
                'extend': True,
                'func': self.split_array,
                'kwargs': {
                    'subkeys': ('crew', ),
                    'id': lambda i: f'person.{i["id"]}',
                    'tmdb_id': 'id', 'thumb': 'profile_path', 'name': 'name', 'gender': 'gender', 'known_for_department': 'known_for_department'}
            }],
            'movie_credits': self.list_person_credits('movie'),
            'tv_credits': self.list_person_credits('tv'),
            'fanart_tv': [{
                'keys': [('fanart_tv', None)],
                'func': self.get_fanart_tv,
            }],
            'budget': [{
                'keys': [('custom', None)],
                'extend': True,
                'func': lambda v: [{'key': 'budget', 'value': f'${float(v):0,.0f}'}]
            }],
            'revenue': [{
                'keys': [('custom', None)],
                'extend': True,
                'func': lambda v: [{'key': 'revenue', 'value': f'${float(v):0,.0f}'}]
            }],
        }

        self.standard_map = {
            'id': ('item', 'tmdb_id'),
            'title': ('item', 'title'),
            'tagline': ('item', 'tagline'),
            'overview': ('item', 'plot'),
            'original_title': ('item', 'originaltitle'),
            'original_name': ('item', 'originaltitle'),
            'status': ('item', 'status'),
            'season_number': ('item', 'season'),
            'episode_number': ('item', 'episode'),
            'number_of_seasons': ('item', 'totalseasons'),
            'number_of_episodes': ('item', 'totalepisodes'),
            'episode_type': ('item', 'status'),
            'biography': ('item', 'biography'),
            'birthday': ('item', 'birthday'),
            'deathday': ('item', 'deathday'),
            'gender': ('item', 'gender'),
            'known_for_department': ('item', 'known_for_department'),
            'place_of_birth': ('item', 'place_of_birth'),
            'profile_path': ('item', 'thumb'),
            'vote_average': ('item', 'rating'),
            'vote_count': ('item', 'votes'),
            'popularity': ('item', 'popularity')
        }

    def dict_person_credits_art(self, tmdb_type, subkey, artkey, aspect):
        return {
            'keys': [('art', None)],
            'extend': True,
            'func': self.split_array,
            'kwargs': {
                'subkeys': (subkey, ),
                'haskeys': (artkey, ),
                'parent_id': lambda i: f'{tmdb_type}.{i["id"]}',
                'icon': artkey,
                'type': lambda _: aspect,
                'aspect_ratio': lambda _: aspect,
                'extension': lambda i: i[artkey].split('.')[-1]}
        }

    def dict_person_credits_member(self, tmdb_type, subkey):
        kwargs = {
            'subkeys': (subkey, ),
            'parent_id': lambda i: f'{tmdb_type}.{i["id"]}',
            'tmdb_id': lambda _: self.tmdb_id}

        if subkey == 'cast':
            kwargs['role'] = 'character'
            kwargs['ordering'] = 'order'

        if subkey == 'crew':
            kwargs['role'] = 'job'
            kwargs['department'] = 'department'

        return {
            'keys': [(f'{subkey}member', None)],
            'extend': True,
            'func': self.split_array,
            'kwargs': kwargs
        }

    def dict_person_credits_baseitem(self, tmdb_type, subkey):
        return {
            'keys': [('baseitem', None)],
            'extend': True,
            'func': self.split_array,
            'kwargs': {
                'subkeys': (subkey, ),
                'id': lambda i: f'{tmdb_type}.{i["id"]}',
                'mediatype': lambda _: 'movie' if tmdb_type == 'movie' else 'tvshow',
                'expiry': lambda _: 0}
        }

    def dict_person_credits_tmdbtype(self, tmdb_type, subkey):
        mediatype = 'movie' if tmdb_type == 'movie' else 'tvshow'
        premiered = 'release_date' if mediatype == 'movie' else 'first_air_date'
        titlename = 'title' if mediatype == 'movie' else 'name'
        return {
            'keys': [(mediatype, None)],
            'extend': True,
            'func': self.split_array,
            'kwargs': {
                'subkeys': (subkey, ),
                'id': lambda i: f'{tmdb_type}.{i["id"]}',
                'tmdb_id': 'id',
                'year': lambda i: int(i[premiered][0:4]),
                'premiered': premiered,
                'plot': 'overview',
                'title': titlename,
                'originaltitle': 'original_title',
                'rating': 'vote_average',
                'votes': 'vote_count',
                'popularity': 'popularity'
            }
        }

    def list_person_credits_subkey(self, tmdb_type, subkey):
        return [
            self.dict_person_credits_member(tmdb_type, subkey),
            self.dict_person_credits_baseitem(tmdb_type, subkey),
            self.dict_person_credits_tmdbtype(tmdb_type, subkey),
            self.dict_person_credits_art(tmdb_type, subkey, 'poster_path', 'posters'),
            self.dict_person_credits_art(tmdb_type, subkey, 'backdrop_path', 'backdrops'),
        ]

    def list_person_credits(self, tmdb_type):
        return self.list_person_credits_subkey(tmdb_type, 'cast') + self.list_person_credits_subkey(tmdb_type, 'crew')

    @staticmethod
    def get_empty_item():
        return {
            'item': BlankNoneDict(),
            'genre': (),
            'country': (),
            'company': [],
            'studio': (),
            'broadcaster': [],
            'network': (),
            'provider': (),
            'certification': (),
            'service': [],
            'video': (),
            'baseitem': [],
            'movie': [],
            'tvshow': [],
            'season': [],
            'episode': [],
            'collection': [],
            'castmember': [],
            'crewmember': [],
            'unique_id': [],
            'custom': [],
            'person': [],
            'fanart_tv': [],
            'art': [],
        }

    def get_info(self, data, **kwargs):
        self.item = self.get_empty_item()
        self.item = self.map_item(self.item, data)
        return self.item
