#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.api.mapping import _ItemMapper
from collections import namedtuple


ExtendedMap = namedtuple("ExtendedMap", "base unique_id overwrite data")


# Consts for wrangling FTV artwork into shape
FTV_WITHOUT_SEASONS = 0
FTV_TVSHOWS_SEASONS = 1
FTV_SEASONS_SEASONS = 2


def get_blanks_none(i):
    """
    Convert empty strings to nulls
    """
    return i if i or i == 0 else None


class ItemMapperMethods:
    @staticmethod
    def get_runtime(i, *args, **kwargs):
        if isinstance(i, list):
            i = i[0]
        try:
            return int(i) * 60
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def add_art_type(item_id, image_path, image_type, ratio_type):
        from tmdbhelper.lib.addon.consts import IMAGEPATH_ASPECTRATIO
        return {
            'parent_id': item_id,
            'aspect_ratio': IMAGEPATH_ASPECTRATIO.index(ratio_type),
            'icon': get_blanks_none(image_path),
            'type': image_type,
            'extension': get_blanks_none(image_path.split('.')[-1] if image_path else None),
        }

    @staticmethod
    def get_configured_item(i, blanks=True, **kwargs):

        def get_item(i, v):
            try:
                if not callable(v):
                    return i.get(v)
                return v(i)
            except (TypeError, KeyError, IndexError, ValueError):
                return

        configured_items = {k: get_blanks_none(get_item(i, v)) for k, v in kwargs.items()}
        return configured_items if blanks else {k: v for k, v in configured_items.items() if k and v}

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

        def check_item(i):
            for k in haskeys:
                try:
                    if not i[k]:
                        return
                except (TypeError, KeyError, IndexError, ValueError):
                    return
            return i

        items = [i for i in items if check_item(i)] if haskeys else items
        return [ItemMapperMethods.get_configured_item(i, **kwargs) for i in items]

    @staticmethod
    def get_episode_type(i, **kwargs):
        episode_type = i['episode_type']
        season_number = i['season_number']
        episode_number = i['episode_number']
        if season_number == 0:
            return 'special'
        if episode_number == 1:
            return 'series_premiere' if season_number == 1 else 'season_premiere'
        if episode_type == 'finale':
            return 'season_finale'  # TODO: Series finale currently calculated as part of last_aired (checks status as cancelled/ended and assumes last_aired episode is finale)
        if episode_type == 'mid_season':
            return 'mid_season_finale'  # TODO: Calculate mid season premiere (might be a real pain to do)
        return 'standard'

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
    def get_translations(items, **kwargs):
        if not items:
            return
        results = items.get('translations')
        if not results:
            return
        data = [
            {
                'iso_country': get_blanks_none(translation['iso_3166_1']),
                'iso_language': get_blanks_none(translation['iso_639_1']),
                'title': get_blanks_none(translation['data'].get('title') or translation['data'].get('name')),
                'plot': get_blanks_none(translation['data'].get('overview')),
                'tagline': get_blanks_none(translation['data'].get('tagline')),
            } for translation in results
        ]
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

    def get_belongs_to_collection(self, i, **kwargs):
        data = []

        item_id = f"movie.{self.tmdb_id}"
        collection_id = f"collection.{i['id']}"

        collection_item = ItemMapperMethods.get_configured_item(i, **{
            'tmdb_id': 'id',
            'title': 'name',
        })
        collection_item['id'] = collection_id
        data.append(ExtendedMap('collection', collection_id, False, collection_item))

        for image_path, image_type, ratio_type in (
            ('poster_path', 'posters', 'poster'),
            ('backdrop_path', 'backdrops', 'landscape')
        ):
            image_path = i.get(image_path)
            if not image_path:
                continue

            data.append(ExtendedMap('art', image_path, False, ItemMapperMethods.add_art_type(
                item_id=item_id,
                image_path=image_path,
                image_type=image_type,
                ratio_type=ratio_type
            )))

        data.append(ExtendedMap('belongs', item_id, False, {
            'id': item_id,
            'parent_id': collection_id,
        }))

        data.append(ExtendedMap('baseitem', collection_id, False, {
            'id': collection_id,
            'mediatype': 'set',
            'expiry': 0,
            'language': self.language,
        }))

        return data

    def get_collection(self, collection_object, **kwargs):
        data = []

        if not collection_object:
            return data

        collection_id = f"collection.{collection_object['id']}"

        for i in (collection_object.get('parts') or []):
            data.extend(self.get_media_item_data(i, 'movie'))
            data.append(ExtendedMap('belongs', f'movie.{i["id"]}', False, {
                'id': f'movie.{i["id"]}',
                'parent_id': collection_id,
            }))

        return data

    def get_parts(self, parts, **kwargs):
        data = []

        if not parts:
            return data

        collection_id = f"collection.{self.tmdb_id}"

        for i in parts:
            data.extend(self.get_media_item_data(i, 'movie'))
            data.append(ExtendedMap('belongs', f'movie.{i["id"]}', False, {
                'id': f'movie.{i["id"]}',
                'parent_id': collection_id,
            }))

        return data

    def get_creators(self, items, **kwargs):
        data = []

        for i in items:
            item_id = f'person.{i["id"]}'
            tmdb_id = i['id']

            data.append(ExtendedMap('crewmember', item_id, False, {
                'tmdb_id': tmdb_id,
                'role': 'Creator',
                'department': 'Creator',
            }))

            person_item = ItemMapperMethods.get_configured_item(i, **{
                'name': 'name',
                'gender': 'gender',
            })
            person_item['id'] = item_id
            person_item['tmdb_id'] = tmdb_id
            data.append(ExtendedMap('person', item_id, False, person_item))

            if i.get('profile_path'):
                artwork = ItemMapperMethods.add_art_type(
                    item_id=item_id,
                    image_path=i['profile_path'],
                    image_type='profiles',
                    ratio_type='poster')
                data.append(ExtendedMap('art', artwork['icon'], False, artwork))

            data.append(ExtendedMap('baseitem', item_id, False, {
                'id': item_id,
                'mediatype': 'person',
                'expiry': 0,
                'language': self.language,
            }))

        return data

    def get_episode_to_air(self, i, **kwargs):
        data = []

        item_id = f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}'
        season_id = f'tv.{self.tmdb_id}.{i["season_number"]}'
        tvshow_id = f'tv.{self.tmdb_id}'

        episode_item = ItemMapperMethods.get_configured_item(i, **{
            'episode': 'episode_number',
            'premiered': 'air_date',
            'title': 'name',
            'plot': 'overview',
            'rating': 'vote_average',
            'votes': 'vote_count',
            'status': lambda i: self.get_episode_type(i),
            'duration': lambda i: self.get_runtime(i['runtime'])
        })
        episode_item['id'] = item_id
        episode_item['season_id'] = season_id
        episode_item['tvshow_id'] = tvshow_id

        if not self.data.get('in_production') and not self.data.get('next_episode_to_air'):
            episode_item['status'] = 'series_finale'

        data.append(ExtendedMap('episode', item_id, False, episode_item))

        data.append(ExtendedMap('season', season_id, False, {
            'id': season_id,
            'tvshow_id': tvshow_id,
            'season': i['season_number'],
        }))

        data.append(ExtendedMap('baseitem', item_id, False, {
            'id': item_id,
            'mediatype': 'episode',
            'expiry': 0,
            'language': self.language,
        }))

        data.append(ExtendedMap('baseitem', season_id, False, {
            'id': season_id,
            'mediatype': 'season',
            'expiry': 0,
            'language': self.language,
        }))

        if i.get('still_path'):
            artwork = ItemMapperMethods.add_art_type(
                item_id=item_id,
                image_path=i['still_path'],
                image_type='stills',
                ratio_type='landscape')
            data.append(ExtendedMap('art', artwork['icon'], False, artwork))

        # Use last/next aired duration if available for tvshow duration
        if episode_item.get('duration') and not self.item['item'].get('duration'):
            self.item['item']['duration'] = episode_item['duration']

        return data

    credits_mappings = (
        ('cast', 'castmember', {'ordering': 'order', 'role': 'character', 'appearances': 'total_episode_count'}, 'roles'),
        ('crew', 'crewmember', {'department': 'department', 'role': 'job', 'appearances': 'total_episode_count'}, 'jobs'),
        ('guest_stars', 'castmember', {'ordering': 'order', 'role': 'character', 'appearances': 'total_episode_count'}, 'roles'),
    )

    def get_credits(self, items, **kwargs):
        return self.get_credits_data(items, False)

    def get_aggregate_credits(self, items, **kwargs):
        return self.get_credits_data(items, True)

    def get_credits_data(self, items, aggregrate=False):
        data = []
        for subkey, mapkey, config, jobkey in self.credits_mappings:

            for i in (items.get(subkey) or []):
                item_id = f'person.{i["id"]}'
                tmdb_id = i['id']

                data.append(ExtendedMap('baseitem', item_id, False, {
                    'id': item_id,
                    'mediatype': 'person',
                    'expiry': 0,
                    'language': self.language,
                }))

                jobs = (i.get(jobkey) or []) if aggregrate else [i]

                for j in jobs:
                    credit_item = ItemMapperMethods.get_configured_item(i, **config)
                    credit_item.update(ItemMapperMethods.get_configured_item(j, blanks=False, **config))
                    credit_item['tmdb_id'] = tmdb_id
                    data.append(ExtendedMap(mapkey, j.get('credit_id'), False, credit_item))

                person_item = ItemMapperMethods.get_configured_item(i, **{
                    'name': 'name',
                    'gender': 'gender',
                    'known_for_department': 'known_for_department',
                })
                person_item['id'] = item_id
                person_item['tmdb_id'] = tmdb_id
                data.append(ExtendedMap('person', item_id, False, person_item))

                if i.get('profile_path'):
                    artwork = ItemMapperMethods.add_art_type(
                        item_id=item_id,
                        image_path=i['profile_path'],
                        image_type='profiles',
                        ratio_type='poster')
                    data.append(ExtendedMap('art', artwork['icon'], False, artwork))

        return data

    def get_person_movie_credits_data(self, items):
        return self.get_person_credits_data(items, 'movie')

    def get_person_tv_credits_data(self, items):
        return self.get_person_credits_data(items, 'tv')

    def get_person_credits_data(self, items, tmdb_type='movie'):
        data = []

        mappings = (
            ('cast', 'castmember', {'ordering': 'order', 'role': 'character'}),
            ('crew', 'crewmember', {'department': 'department', 'role': 'job'}),
        )

        for subkey, mapkey, config in mappings:
            credits = items.get(subkey) or []
            for i in credits:
                data.extend(self.get_media_item_data(i, tmdb_type))

                credit_item = ItemMapperMethods.get_configured_item(i, **config)
                credit_item['parent_id'] = f'{tmdb_type}.{i["id"]}'
                credit_item['tmdb_id'] = self.tmdb_id
                data.append(ExtendedMap(mapkey, i.get('credit_id'), False, credit_item))

        return data

    def get_media_item_data(self, i, tmdb_type, **additional_params):
        data = []

        item_id = f'{tmdb_type}.{i["id"]}'

        mediatype = 'movie' if tmdb_type == 'movie' else 'tvshow'
        premiered = 'release_date' if mediatype == 'movie' else 'first_air_date'
        titlename = 'title' if mediatype == 'movie' else 'name'

        media_item = ItemMapperMethods.get_configured_item(i, **{
            'year': lambda i: int(i[premiered][0:4]),
            'premiered': premiered,
            'plot': 'overview',
            'title': titlename,
            'originaltitle': 'original_title',
            'rating': 'vote_average',
            'votes': 'vote_count',
            'popularity': 'popularity'

        })
        media_item['id'] = item_id
        media_item['tmdb_id'] = i['id']
        media_item.update(additional_params)
        data.append(ExtendedMap(mediatype, item_id, False, media_item))

        data.append(ExtendedMap('baseitem', item_id, False, {
            'id': item_id,
            'mediatype': mediatype,
            'expiry': 0,
            'language': self.language,
        }))

        for image_path, image_type, ratio_type in (
            ('poster_path', 'posters', 'poster'),
            ('backdrop_path', 'backdrops', 'landscape')
        ):
            image_path = i.get(image_path)
            if not image_path:
                continue
            data.append(ExtendedMap('art', image_path, False, ItemMapperMethods.add_art_type(
                item_id=item_id,
                image_path=image_path,
                image_type=image_type,
                ratio_type=ratio_type
            )))
        return data

    def get_episodes(self, items, **kwargs):
        data = []

        for i in items:
            item_id = f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}'
            season_id = f'tv.{self.tmdb_id}.{i["season_number"]}'
            tvshow_id = f'tv.{self.tmdb_id}'

            episode_item = ItemMapperMethods.get_configured_item(i, **{
                'episode': 'episode_number',
                'year': lambda i: int(i['air_date'][0:4]),
                'premiered': 'air_date',
                'title': 'name',
                'plot': 'overview',
                'rating': 'vote_average',
                'votes': 'vote_count',
                'status': lambda i: self.get_episode_type(i),
                'duration': lambda i: self.get_runtime(i['runtime'])
            })
            episode_item['id'] = item_id
            episode_item['season_id'] = season_id
            episode_item['tvshow_id'] = tvshow_id

            data.append(ExtendedMap('episode', item_id, True, episode_item))

            if i.get('still_path'):
                artwork = ItemMapperMethods.add_art_type(
                    item_id=item_id,
                    image_path=i['still_path'],
                    image_type='stills',
                    ratio_type='landscape')
                data.append(ExtendedMap('art', artwork['icon'], False, artwork))

            data.append(ExtendedMap('baseitem', item_id, False, {
                'id': item_id,
                'mediatype': 'episode',
                'expiry': 0,
                'language': self.language,
            }))

        return data

    def get_seasons(self, items, **kwargs):
        data = []

        for i in items:
            item_id = f'tv.{self.tmdb_id}.{i["season_number"]}'
            tvshow_id = f'tv.{self.tmdb_id}'

            season_item = ItemMapperMethods.get_configured_item(i, **{
                'season': 'season_number',
                'year': lambda i: int(i['air_date'][0:4]),
                'premiered': 'air_date',
                'title': 'name',
                'plot': 'overview',
                'rating': 'vote_average',
            })
            season_item['id'] = item_id
            season_item['tvshow_id'] = tvshow_id

            data.append(ExtendedMap('season', item_id, True, season_item))

            if i.get('poster_path'):
                artwork = ItemMapperMethods.add_art_type(
                    item_id=item_id,
                    image_path=i['poster_path'],
                    image_type='posters',
                    ratio_type='poster')
                data.append(ExtendedMap('art', artwork['icon'], False, artwork))

            data.append(ExtendedMap('baseitem', item_id, False, {
                'id': item_id,
                'mediatype': 'season',
                'expiry': 0,
                'language': self.language
            }))

        return data

    def get_fanart_tv(self, items, **kwargs):
        if not items:
            return

        # FTV artwork key name, type to map it to, art_has_seasons
        # Set art_has_seasons to FTV_TVSHOWS_SEASONS for artwork where fanarttv intends "season=all" to be "tvshow" artwork
        # Set art_has_seasons to FTV_SEASONS_SEASONS for artwork where fanarttv intends "season=all" to be "season" artwork
        art_types = {
            'movieposter': ('poster', FTV_WITHOUT_SEASONS),
            'moviebackground': ('fanart', FTV_WITHOUT_SEASONS),
            'moviethumb': ('landscape', FTV_WITHOUT_SEASONS),
            'moviebanner': ('banner', FTV_WITHOUT_SEASONS),
            'hdmovieclearart': ('clearart', FTV_WITHOUT_SEASONS),
            'movieclearart': ('clearart', FTV_WITHOUT_SEASONS),
            'hdmovielogo': ('clearlogo', FTV_WITHOUT_SEASONS),
            'movielogo': ('clearlogo', FTV_WITHOUT_SEASONS),
            'moviedisc': ('discart', FTV_WITHOUT_SEASONS),
            'tvposter': ('poster', FTV_WITHOUT_SEASONS),
            'tvthumb': ('landscape', FTV_WITHOUT_SEASONS),
            'tvbanner': ('banner', FTV_WITHOUT_SEASONS),
            'hdclearart': ('clearart', FTV_WITHOUT_SEASONS),
            'clearart': ('clearart', FTV_WITHOUT_SEASONS),
            'hdtvlogo': ('clearlogo', FTV_WITHOUT_SEASONS),
            'clearlogo': ('clearlogo', FTV_WITHOUT_SEASONS),
            'characterart': ('characterart', FTV_WITHOUT_SEASONS),
            'showbackground': ('fanart', FTV_TVSHOWS_SEASONS),
            'seasonposter': ('poster', FTV_SEASONS_SEASONS),
            'seasonbanner': ('banner', FTV_SEASONS_SEASONS),
            'seasonthumb': ('landscape', FTV_SEASONS_SEASONS),
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
                icon = get_blanks_none(art_item['url'])

                if not icon:
                    continue

                item = {
                    'icon': icon,
                    'iso_language': get_blanks_none(art_item.get('lang')),
                    'likes': get_blanks_none(art_item.get('likes')),
                    'type': get_blanks_none(art_type),
                    'quality': get_blanks_none(quality),
                    'extension': get_blanks_none(icon.split('.')[-1] if icon else None),
                }

                if art_has_seasons:
                    # Some artwork on FanartTV uses season=all to indicate tvshow artwork
                    # While other artwork types use season=all to indicate season artwork for an "all" season...
                    # Do some gymnastics here to workaround this mess of conflated types
                    snum = (art_item.get('season') or 'all')

                    # Set "All Seasons" artwork to -1 season so we dont pull it in for a tvshow if it is really intended to be an "all" season type
                    if snum == 'all' and art_has_seasons == FTV_SEASONS_SEASONS:
                        snum = -1

                    # Set season artwork with a number ot season type
                    if snum != 'all':
                        parent_id = f'tv.{self.tmdb_id}.{snum}'

                        item['parent_id'] = parent_id

                        data.append(ExtendedMap('baseitem', parent_id, False, {
                            'id': parent_id,
                            'mediatype': 'season',
                            'expiry': 0,
                            'language': self.language,
                        }))

                data.append(ExtendedMap('fanart_tv', icon, True, item))

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
            return []

        data = []

        for artwork_type, artworks in items.items():
            for artwork in artworks:
                path = artwork['file_path']
                data.append(
                    ExtendedMap('art', get_blanks_none(path), True, {
                        'aspect_ratio': ItemMapperMethods.get_aspect_ratio(artwork['aspect_ratio']),
                        'quality': int((artwork['width'] * artwork['height']) // 200000),  # Quality integer to nearest fifth of a megapixel
                        'iso_language': get_blanks_none(artwork['iso_639_1']),
                        'icon': get_blanks_none(path),
                        'type': get_blanks_none(artwork_type),
                        'extension': get_blanks_none(path.split('.')[-1] if path else None),
                        'rating': int(artwork['vote_average'] * 100),
                        'votes': get_blanks_none(artwork['vote_count'])
                    })
                )

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
    def get_custom_time(duration, name='duration'):
        if not duration:
            return {}
        minutes = duration // 60 % 60
        hours = duration // 60 // 60
        totalmin = duration // 60
        infoproperties = {
            f'{name}.H': hours,
            f'{name}.M': minutes,
            f'{name}.mins': totalmin,
            f'{name}.HHMM': f'{hours:02d}:{minutes:02d}',
        }
        return infoproperties

    @staticmethod
    def get_custom_date(air_date, name):
        from tmdbhelper.lib.addon.plugin import get_infolabel
        from tmdbhelper.lib.addon.tmdate import format_date_obj, convert_timestamp, get_days_to_air
        air_date_obj = convert_timestamp(air_date, time_fmt="%Y-%m-%d", time_lim=10, utc_convert=False)

        if not air_date_obj:
            return {}

        infoproperties = {
            f'{name}': format_date_obj(air_date_obj, region_fmt='dateshort'),
            f'{name}.long': format_date_obj(air_date_obj, region_fmt='datelong'),
            f'{name}.short': format_date_obj(air_date_obj, "%d %b"),
            f'{name}.day': format_date_obj(air_date_obj, "%A"),
            f'{name}.day_short': format_date_obj(air_date_obj, "%a"),
            f'{name}.year': format_date_obj(air_date_obj, "%Y"),
            f'{name}.custom': format_date_obj(air_date_obj, get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y'),
            f'{name}.original': air_date,
        }

        days_to_air, is_aired = get_days_to_air(air_date_obj)
        days_to_air_name = f'{name}.days_from_aired' if is_aired else f'{name}.days_until_aired'

        infoproperties[days_to_air_name] = str(days_to_air)
        return infoproperties

    @staticmethod
    def get_custom_property(key, value):
        return [ExtendedMap('custom', key, False, {'key': key, 'value': value})]

    @staticmethod
    def get_art_property(path, art_type):
        return [ExtendedMap('art', path, False, {
            'icon': path,
            'type': art_type,
            'extension': path.split('.')[-1] if path else None
        })]


class BlankNoneDict(dict):
    def __missing__(self, key):
        return None


class ItemMapper(_ItemMapper, ItemMapperMethods):
    def __init__(self, language, tmdb_id):
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
            'translations': [{
                'keys': [('translation', None)],
                'func': self.get_translations,
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
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id', 'name': 'name', 'logo': 'logo_path', 'country': 'origin_country'}
            }],
            'networks': [{
                'keys': [('network', None)],
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id'}}, {
                # ---
                'keys': [('broadcaster', None)],
                'func': self.split_array,
                'kwargs': {'tmdb_id': 'id', 'name': 'name', 'logo': 'logo_path', 'country': 'origin_country'}
            }],
            'watch/providers': [{
                'keys': [('provider', None)],
                'func': self.get_providers}, {
                # ---
                'keys': [('service', None)],
                'func': self.get_providers,
                'kwargs': {'service': True}
            }],
            'external_ids': [{
                'keys': [('unique_id', None)],
                'func': self.get_unique_ids,
            }],
            'videos': [{
                'keys': [('video', None)],
                'func': self.get_video,
            }],
            'last_episode_to_air': [{
                'keys': [('item', f'last_episode_to_air_id')],
                'func': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}'
            }],
            'next_episode_to_air': [{
                'keys': [('item', f'next_episode_to_air_id')],
                'func': lambda i: f'tv.{self.tmdb_id}.{i["season_number"]}.{i["episode_number"]}'
            }],
        }

        self.extended_map = {
            'budget': lambda v: self.get_custom_property('budget', f'${float(v):0,.0f}'),
            'revenue': lambda v: self.get_custom_property('revenue', f'${float(v):0,.0f}'),
            'original_language': lambda v: self.get_custom_property('original_language', v),
            'homepage': lambda v: self.get_custom_property('homepage', v),
            'poster_path': lambda v: self.get_art_property(v, 'posters'),
            'backdrop_path': lambda v: self.get_art_property(v, 'backdrops'),
            'profile_path': lambda v: self.get_art_property(v, 'profiles'),
            'images': self.get_art,
            'fanart_tv': self.get_fanart_tv,
            'belongs_to_collection': self.get_belongs_to_collection,
            'collection': self.get_collection,
            'parts': self.get_parts,
            'seasons': self.get_seasons,
            'episodes': self.get_episodes,
            'created_by': self.get_creators,
            'credits': self.get_credits,
            'aggregate_credits': self.get_aggregate_credits,
            'last_episode_to_air': self.get_episode_to_air,  # Also mapped in advanced properties for item id
            'next_episode_to_air': self.get_episode_to_air,  # Also mapped in advanced properties for item id
            'movie_credits': self.get_person_movie_credits_data,
            'tv_credits': self.get_person_tv_credits_data,
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
            'biography': ('item', 'biography'),
            'birthday': ('item', 'birthday'),
            'deathday': ('item', 'deathday'),
            'gender': ('item', 'gender'),
            'known_for_department': ('item', 'known_for_department'),
            'place_of_birth': ('item', 'place_of_birth'),
            'vote_average': ('item', 'rating'),
            'vote_count': ('item', 'votes'),
            'popularity': ('item', 'popularity')
        }

        self.language = language
        self.tmdb_id = tmdb_id

    def map_dict(self, item, data):

        map_dict = {}

        for k, v in data.items():

            # Skip blank values
            if v in (None, ''):
                continue

            # Only some values need extended mappings
            if k not in self.extended_map:
                continue

            # Make sure the function outputs data
            output = self.extended_map[k](v)
            if not output:
                continue

            for i in output:

                # Make sure unique_id has a value we can use as an ID
                if not i.unique_id:
                    continue

                dictionary = map_dict.setdefault(i.base, {})

                # Overwrite set so just overwrite and move on
                if i.overwrite:
                    dictionary[i.unique_id] = i.data
                    continue

                # ID not mapped yet so write it and move on
                if i.unique_id not in dictionary:
                    dictionary[i.unique_id] = i.data
                    continue

                # Only write new values
                for ik, iv in i.data.items():
                    if not dictionary[i.unique_id].get(ik):  # Dont write over existing values
                        continue
                    dictionary[i.unique_id][ik] = iv  # No value set so update it

        for key, dictionary in map_dict.items():
            item[key] = tuple([d for d in dictionary.values()])

        return item

    @staticmethod
    def get_empty_item():
        return {

            # Default mappings
            'item': BlankNoneDict(),
            'genre': (),
            'country': (),
            'company': (),
            'studio': (),
            'broadcaster': (),
            'network': (),
            'provider': (),
            'certification': (),
            'service': (),
            'video': (),
            'unique_id': (),
            'translation': (),

            # Dictionary mappings
            'custom': (),
            'art': (),
            'baseitem': (),
            'fanart_tv': (),
            'collection': (),
            'movie': (),
            'tvshow': (),
            'season': (),
            'episode': (),
            'person': (),
            'crewmember': (),
            'castmember': (),
            'belongs': (),
        }

    def get_info(self, data, **kwargs):
        self.data = data
        self.item = self.get_empty_item()
        self.item = self.map_item(self.item, data)
        self.item = self.map_dict(self.item, data)

        # from tmdbhelper.lib.files.futils import dumps_to_file
        # dumps_to_file(
        #     {'data': self.data, 'item': self.item},
        #     'log_data', f'mappings_{self.tmdb_id}_{data["name"]}.json', join_addon_data=True)

        return self.item
