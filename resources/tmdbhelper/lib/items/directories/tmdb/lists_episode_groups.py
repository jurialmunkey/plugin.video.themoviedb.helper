from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from jurialmunkey.parser import try_int


def _image(path):
    if not path:
        return None

    path = str(path)

    if path.startswith(('http://', 'https://')):
        return path

    return 'https://image.tmdb.org/t/p/original{}'.format(path)


def _get_show_details(tmdb_api, tmdb_id):
    try:
        show = tmdb_api.get_response_json('tv', tmdb_id) or {}
    except Exception:
        show = {}

    try:
        images = tmdb_api.get_response_json(
            'tv',
            tmdb_id,
            'images'
        ) or {}
    except Exception:
        images = {}

    logos = images.get('logos') or []
    logo_path = None

    for language in (None, 'en'):
        for logo in logos:
            if logo.get('iso_639_1') == language:
                logo_path = logo.get('file_path')

                if logo_path:
                    break

        if logo_path:
            break

    if not logo_path:
        for logo in logos:
            logo_path = logo.get('file_path')

            if logo_path:
                break

    if logo_path:
        show['logo_path'] = logo_path

    return show


class ListEpisodeGroups(ContainerDirectory):

    def get_items(self, tmdb_id, **kwargs):
        data = self.tmdb_api.get_response_json(
            'tv',
            tmdb_id,
            'episode_groups'
        ) or {}

        results = data.get('results') or []
        show = _get_show_details(self.tmdb_api, tmdb_id)

        self.container_content = 'tvshows'

        show_title = (
            show.get('name')
            or show.get('original_name')
            or ''
        )

        genres = [
            genre.get('name')
            for genre in show.get('genres') or []
            if genre.get('name')
        ]

        studio = [
            network.get('name')
            for network in show.get('networks') or []
            if network.get('name')
        ]

        art = {}

        if show.get('poster_path'):
            art['poster'] = _image(show.get('poster_path'))

        if show.get('backdrop_path'):
            art['fanart'] = _image(show.get('backdrop_path'))

        if show.get('logo_path'):
            logo = _image(show.get('logo_path'))
            art['clearlogo'] = logo
            art['logo'] = logo

        items = []

        for group in results:
            group_id = group.get('id')

            if not group_id:
                continue

            group_name = group.get('name') or str(group_id)

            items.append({
                'label': group_name,

                'infolabels': {
                    'title': group_name,
                    'mediatype': 'video',
                    'plot': (
                        group.get('description')
                        or show.get('overview')
                        or ''
                    ),
                    'tvshowtitle': show_title,
                    'year': (
                        str(show.get('first_air_date', ''))[:4]
                        if show.get('first_air_date')
                        else ''
                    ),
                    'premiered': show.get('first_air_date') or '',
                    'rating': show.get('vote_average') or 0,
                    'votes': show.get('vote_count') or 0,
                    'genre': genres,
                },

                'infoproperties': {
                    'episode_group_id': group_id,
                    'group_count': group.get('group_count') or 0,
                    'episode_group_type': group.get('type'),
                    'episode_group_name': group_name,
                    'episode_group_virtual': 'true',
                    'tmdb_id': tmdb_id,
                    'tvshow.tmdb': tmdb_id,
                    'tmdb_type': 'tv',
                    'tvshowtitle': show_title,
                    'studio': studio,
                },

                'unique_ids': {
                    'tmdb': group_id,
                    'tvshow.tmdb': tmdb_id,
                },

                'art': art,

                'params': {
                    'info': 'episode_group_seasons',
                    'tmdb_type': 'tv',
                    'tmdb_id': tmdb_id,
                    'group_id': group_id,
                    'group_type': group.get('type'),
                },
            })

        return items


class ListEpisodeGroupSeasons(ContainerDirectory):

    def get_items(self, tmdb_id, group_id, group_type=None, **kwargs):
        data = self.tmdb_api.get_response_json(
            'tv',
            'episode_group',
            group_id
        ) or {}

        groups = data.get('groups') or []
        group_type = try_int(group_type)

        self.container_content = 'seasons'

        if not groups:
            return []

        show = _get_show_details(self.tmdb_api, tmdb_id)

        show_title = (
            show.get('name')
            or show.get('original_name')
            or ''
        )

        original_title = (
            show.get('original_name')
            or show_title
        )

        premiered = show.get('first_air_date') or ''
        year = premiered[:4] if premiered else ''

        genres = [
            genre.get('name')
            for genre in show.get('genres') or []
            if genre.get('name')
        ]

        status = show.get('status') or ''
        rating = show.get('vote_average') or 0
        votes = show.get('vote_count') or 0
        overview = show.get('overview') or ''

        poster = _image(show.get('poster_path'))
        fanart = _image(show.get('backdrop_path'))
        logo = _image(show.get('logo_path'))

        indexed_groups = list(enumerate(groups))

        def sort_key(item):
            index, group = item

            try:
                order = int(group.get('order'))
            except (TypeError, ValueError):
                order = index + 1

            return order, index

        indexed_groups.sort(key=sort_key)

        items = []

        for display_position, (original_position, group) in enumerate(
            indexed_groups,
            1
        ):
            if not group:
                continue

            group_name = group.get('name') or 'Group {}'.format(
                display_position
            )

            episodes = group.get('episodes') or []

            try:
                group_order = int(group.get('order'))
            except (TypeError, ValueError):
                group_order = display_position

            # Use a separate virtual season range to avoid collisions
            # with real TMDB seasons.
            virtual_season = 1000 + display_position

            infolabels = {
                'title': group_name,
                'label': group_name,
                'tvshowtitle': show_title,
                'originaltitle': original_title,
                'plot': group.get('description') or overview,
                'premiered': premiered,
                'firstaired': premiered,
                'year': year,
                'rating': rating,
                'votes': votes,
                'genre': genres,
                'status': status,
                'mediatype': 'season',
                'season': virtual_season,
            }

            infoproperties = {
                'episode_group_id': group_id,
                'episode_group_position': display_position - 1,
                'episode_group_original_position': original_position,
                'episode_group_order': group_order,
                'episode_group_virtual_season': virtual_season,
                'episode_group_type': group_type,
                'episode_group_name': group_name,
                'totalepisodes': len(episodes),
                'episode_group_virtual': 'true',
                'tmdb_id': tmdb_id,
                'tvshow.tmdb': tmdb_id,
                'tvshowtitle': show_title,
                'originaltitle': original_title,
            }

            if logo:
                infoproperties['tmdb_logo_path'] = show.get('logo_path')

            art = {}

            if poster:
                art['poster'] = poster

            if fanart:
                art['fanart'] = fanart
                art['landscape'] = fanart

            if logo:
                art['clearlogo'] = logo
                art['logo'] = logo

            items.append({
                'label': group_name,
                'infolabels': infolabels,
                'infoproperties': infoproperties,

                'unique_ids': {
                    'tvshow.tmdb': tmdb_id,
                },

                'art': art,

                'params': {
                    'info': 'episode_group_episodes',
                    'tmdb_type': 'tv',
                    'tmdb_id': tmdb_id,
                    'group_id': group_id,
                    'position': original_position,
                    'group_type': group_type,
                    'group_name': group_name,
                    'season': virtual_season,
                },
            })

        return items


class ListEpisodeGroupEpisodes(ContainerDirectory):

    def _get_season_data(self, tmdb_id, season, cache):
        season = try_int(season)

        if season is None:
            return {}

        if season in cache:
            return cache[season]

        try:
            data = self.tmdb_api.get_response_json(
                'tv',
                tmdb_id,
                'season',
                season
            ) or {}
        except Exception:
            data = {}

        cache[season] = data

        return data

    def _get_factory_items(self, tmdb_id, season, cache):
        season = try_int(season)

        if season is None:
            return []

        if season in cache:
            return cache[season]

        try:
            factory = BaseViewFactory(
                'episodes',
                'tv',
                tmdb_id,
                season=season
            )
            items = factory.data or []
        except Exception:
            items = []

        cache[season] = items

        return items

    def _find_base_item(
        self,
        tmdb_id,
        season,
        episode,
        episode_id,
        cache
    ):
        items = self._get_factory_items(
            tmdb_id,
            season,
            cache
        )

        episode_id = try_int(episode_id)
        season = try_int(season)
        episode = try_int(episode)

        for item in items:
            unique_ids = item.get('unique_ids') or {}

            if (
                episode_id is not None
                and try_int(unique_ids.get('tmdb')) == episode_id
            ):
                return item

        for item in items:
            labels = item.get('infolabels') or {}

            if (
                try_int(labels.get('season')) == season
                and try_int(labels.get('episode')) == episode
            ):
                return item

        return {}

    def _merge_episode(
        self,
        item,
        episode_data,
        show_data,
        episode_id,
        real_season,
        real_episode
    ):
        episode_data = episode_data or {}
        show_data = show_data or {}

        labels = dict(item.get('infolabels') or {})

        if labels.get('title') is None and episode_data.get('name'):
            labels['title'] = episode_data['name']

        if labels.get('plot') is None and episode_data.get('overview'):
            labels['plot'] = episode_data['overview']

        if labels.get('premiered') is None and episode_data.get('air_date'):
            labels['premiered'] = episode_data['air_date']

        if labels.get('rating') is None:
            rating = episode_data.get('vote_average')

            if rating is not None:
                labels['rating'] = rating

        if labels.get('votes') is None:
            votes = episode_data.get('vote_count')

            if votes is not None:
                labels['votes'] = votes

        if labels.get('duration') is None:
            runtime = try_int(episode_data.get('runtime'))

            if runtime:
                labels['duration'] = runtime * 60

        labels['mediatype'] = 'episode'
        item['infolabels'] = labels

        properties = dict(item.get('infoproperties') or {})

        properties.update({
            'tmdb_episode_id': try_int(episode_id),
            'tmdb_season': real_season,
            'tmdb_episode': real_episode,
            'episode_group_real_season': real_season,
            'episode_group_real_episode': real_episode,
            'episode_group_real_episode_id': try_int(episode_id),
        })

        # Episode and series artwork
        art = dict(item.get('art') or {})

        still = _image(episode_data.get('still_path'))

        if still:
            art['thumb'] = still
            art['episode'] = still
            art['landscape'] = still

        poster = _image(show_data.get('poster_path'))

        if poster:
            art['poster'] = poster

        fanart = _image(show_data.get('backdrop_path'))

        if fanart:
            art['fanart'] = fanart

            if not still:
                art['landscape'] = fanart

        logo = _image(show_data.get('logo_path'))

        if logo:
            art['clearlogo'] = logo
            art['logo'] = logo
            properties['tmdb_logo_path'] = show_data.get('logo_path')

        item['art'] = art

        # Real episode ID
        unique_ids = dict(item.get('unique_ids') or {})
        unique_ids['tmdb'] = try_int(episode_id)

        item['unique_ids'] = unique_ids
        item['infoproperties'] = properties

        return item

    def _build_virtual_episode(
        self,
        base_item,
        tmdb_id,
        group_id,
        position,
        group_order,
        episode_id,
        real_season,
        real_episode,
        virtual_season,
        virtual_episode,
        show_data,
        episode_data
    ):
        item = self._merge_episode(
            dict(base_item),
            episode_data,
            show_data,
            episode_id,
            real_season,
            real_episode
        )

        labels = dict(item.get('infolabels') or {})

        labels.update({
            'season': virtual_season,
            'episode': virtual_episode,
            'mediatype': 'episode',
        })

        item['infolabels'] = labels

        params = dict(item.get('params') or {})

        params.update({
            'info': 'details',
            'tmdb_type': 'tv',
            'tmdb_id': tmdb_id,
            'season': virtual_season,
            'episode': virtual_episode,
            'episode_id': try_int(episode_id),
            'tmdb_season': real_season,
            'tmdb_episode': real_episode,
            'episode_group_id': group_id,
            'episode_group_position': position,
            'episode_group_order': group_order,
            'episode_group_virtual': 'true',
        })

        item['params'] = params

        properties = dict(item.get('infoproperties') or {})

        properties.update({
            'episode_group_id': group_id,
            'episode_group_position': position,
            'episode_group_order': group_order,
            'episode_group_virtual': 'true',
            'episode_group_season': virtual_season,
            'episode_group_episode': virtual_episode,
            'tmdb_season': real_season,
            'tmdb_episode': real_episode,
            'tmdb_episode_id': try_int(episode_id),
            'episode_group_real_season': real_season,
            'episode_group_real_episode': real_episode,
            'episode_group_real_episode_id': try_int(episode_id),
        })

        item['infoproperties'] = properties

        return item

    def get_items(
        self,
        tmdb_id,
        group_id,
        position,
        group_type=None,
        **kwargs
    ):
        data = self.tmdb_api.get_response_json(
            'tv',
            'episode_group',
            group_id
        ) or {}

        groups = data.get('groups') or []
        position = try_int(position)

        if (
            position is None
            or position < 0
            or position >= len(groups)
        ):
            return []

        group = groups[position] or {}
        episodes = group.get('episodes') or []

        self.container_content = convert_type(
            'episode',
            'container'
        )

        if not episodes:
            return []

        try:
            group_order = int(group.get('order'))
        except (TypeError, ValueError):
            group_order = position + 1

        season_cache = {}
        factory_cache = {}

        # Fetch show data once for the entire list
        show_data = _get_show_details(
            self.tmdb_api,
            tmdb_id
        )

        items = []

        for virtual_episode, episode in enumerate(episodes, 1):
            episode_id = try_int(episode.get('id'))
            real_season = try_int(episode.get('season_number'))
            real_episode = try_int(episode.get('episode_number'))

            if (
                not episode_id
                or real_season is None
                or real_episode is None
            ):
                continue

            # Get complete data for the real episode
            season_data = self._get_season_data(
                tmdb_id,
                real_season,
                season_cache
            )

            episode_data = next(
                (
                    ep
                    for ep in season_data.get('episodes') or []
                    if try_int(ep.get('id')) == episode_id
                ),
                None
            )

            # Get the original TMDBHelper item
            base_item = self._find_base_item(
                tmdb_id,
                real_season,
                real_episode,
                episode_id,
                factory_cache
            )

            if not base_item:
                base_item = {
                    'label': (
                        episode.get('name')
                        or 'Episode {}'.format(virtual_episode)
                    ),
                    'infolabels': {
                        'mediatype': 'episode',
                    },
                    'infoproperties': {},
                    'unique_ids': {},
                    'art': {},
                    'params': {},
                }

            items.append(
                self._build_virtual_episode(
                    base_item=base_item,
                    tmdb_id=tmdb_id,
                    group_id=group_id,
                    position=position,
                    group_order=group_order,
                    episode_id=episode_id,
                    real_season=real_season,
                    real_episode=real_episode,
                    virtual_season=group_order,
                    virtual_episode=virtual_episode,
                    show_data=show_data,
                    episode_data=episode_data,
                )
            )

        return items