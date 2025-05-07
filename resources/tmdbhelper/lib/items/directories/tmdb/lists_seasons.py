from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting, ADDONPATH
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.items.container import ContainerDirectory
from jurialmunkey.window import get_property
from jurialmunkey.parser import try_int


class ListSeasons(ContainerDirectory):
    hide_unaired = True
    is_cacheonly = False

    def get_special_seasons(self, tmdb_id):
        items = []

        sync = BaseItemFactory('tvshow')
        sync.tmdb_id = try_int(tmdb_id)
        sync.tmdb_type = 'tv'
        sync.common_apis = self
        base_item = sync.data

        if not base_item:
            return items

        # Up Next
        if get_setting('seasons_upnext') and get_property('TraktIsAuth') == 'True':
            upnext_item = self.tmdb_api.mapper.get_info(
                info_item={'title': get_localized(32043)},
                tmdb_type='season',
                base_item=base_item,
                tmdb_id=tmdb_id,
                definition={
                    'info': 'trakt_upnext',
                    'tmdb_type': 'tv',
                    'tmdb_id': str(tmdb_id),
                    'hide_unaired': 'true'
                }
            )
            upnext_item['art']['thumb'] = upnext_item['art']['poster'] = f'{ADDONPATH}/resources/icons/trakt/up-next.png'
            upnext_item['infolabels']['season'] = -1
            upnext_item['infolabels']['episode'] = 0
            upnext_item['infoproperties']['specialseason'] = get_localized(32043)
            upnext_item['infoproperties']['IsSpecial'] = 'true'
            items.append(upnext_item)

        if get_setting('seasons_anticipated') and base_item['infolabels'].get('status') not in ('Ended', 'Canceled') and base_item['infoproperties'].get('next_episode_to_air_id'):
            unaired_item = self.tmdb_api.mapper.get_info(
                info_item={'title': get_localized(32206)},
                tmdb_type='season',
                base_item=base_item,
                tmdb_id=tmdb_id,
                definition={
                    'info': 'flatseasons',
                    'tmdb_type': 'tv',
                    'tmdb_id': str(tmdb_id),
                    'only_unaired': 'true'
                }
            )
            unaired_item['art']['thumb'] = unaired_item['art']['poster'] = f'{ADDONPATH}/resources/icons/themoviedb/episodes.png'
            unaired_item['infolabels']['season'] = -1
            unaired_item['infolabels']['episode'] = 0
            unaired_item['infoproperties']['specialseason'] = get_localized(32206)
            unaired_item['infoproperties']['IsSpecial'] = 'true'
            items.append(unaired_item)

        return items

    def get_items(self, tmdb_id, limit=None, **kwargs):
        filters = {
            'filter_key': 'season',
            'filter_operator': 'gt',
            'filter_value': 0,
        } if not get_setting('seasons_specials') else {}

        sync = BaseViewFactory('seasons', 'tv', tmdb_id, filters=filters, limit=limit)
        self.container_content = convert_type('season', 'container')
        try:
            return sync.data + self.get_special_seasons(tmdb_id)
        except TypeError:
            return []


class ListFlatSeasons(ContainerDirectory):
    is_cacheonly = False

    def get_items(self, tmdb_id, limit=None, **kwargs):

        def pre_sync_parent(tvshow_sync, season):
            mediatype = 'season'
            base_dbc = BaseItemFactory(mediatype)
            base_dbc.mediatype = mediatype
            base_dbc.tmdb_id = try_int(tmdb_id)
            base_dbc.tmdb_type = 'tv'
            base_dbc.season = season
            base_dbc.common_apis = tvshow_sync.common_apis
            return base_dbc.data

        tvshow_sync = BaseViewFactory('seasons', 'tv', tmdb_id)

        for season in tvshow_sync.data:
            try:
                pre_sync_parent(tvshow_sync, season['infolabels']['season'])
            except (AttributeError, TypeError, KeyError):
                continue

        filters = {
            'filter_key': 'season',
            'filter_operator': 'gt',
            'filter_value': 0,
        } if not get_setting('seasons_specials') else {}

        sync = BaseViewFactory('flatseasons', 'tv', tmdb_id, filters=filters, limit=limit)
        self.container_content = convert_type('episode', 'container')

        return sync.data


class ListEpisodes(ContainerDirectory):
    hide_unaired = True
    is_cacheonly = False

    def get_items(self, tmdb_id, season, limit=None, **kwargs):
        try:
            sync = BaseViewFactory('episodes', 'tv', tmdb_id, season=season, filters=self.filters, limit=limit)
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = f'{get_localized(20373)} {season}'
        return sync.data
