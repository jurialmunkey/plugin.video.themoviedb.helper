from tmdbhelper.lib.addon.plugin import convert_type, get_localized, get_setting
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.items.container import ContainerDirectory, ContainerCacheOnlyDirectory
from jurialmunkey.window import get_property
from jurialmunkey.parser import try_int


class ListSeasons(ContainerDirectory):
    hide_unaired = True

    def get_special_seasons(self, tmdb_id):
        items = []

        # Up Next
        if get_setting('seasons_upnext') and get_property('TraktIsAuth', is_type=float):
            sync = BaseViewFactory('upnextseason', 'tv', tmdb_id)

            try:
                if sync.data[0]['infoproperties']['totalepisodes']:
                    items.append(sync.data[0])
            except (KeyError, TypeError, AttributeError):
                pass

        # Anticipated
        if get_setting('seasons_anticipated'):
            sync = BaseViewFactory('anticipatedseason', 'tv', tmdb_id)

            try:
                if sync.data[0]['infoproperties']['totalepisodes']:
                    items.append(sync.data[0])
            except (KeyError, TypeError, AttributeError):
                pass

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


class ListFlatSeasons(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('flatseasons', 'tv', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = get_localized(32040)
        return sync.data


class ListAnticipatedEpisodes(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('anticipatedepisodes', 'tv', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = get_localized(32040)
        return sync.data


class ListEpisodes(ContainerCacheOnlyDirectory):
    hide_unaired = True

    def get_items(self, tmdb_id, season, limit=None, **kwargs):
        sync = BaseViewFactory('episodes', 'tv', tmdb_id, season=season, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('episode', 'container')
        self.plugin_category = f'{get_localized(20373)} {season}'
        return sync.data


class ListSpecifiedEpisodes(ContainerDirectory):

    @staticmethod
    def get_item_details(tmdb_id, season, episode):
        return {
            'infolabels': {
                'mediatype': 'episode',
                'season': try_int(season),
                'episode': try_int(episode),
            },
            'unique_ids': {
                'tmdb': tmdb_id,
                'tvshow.tmdb': tmdb_id
            },
            'params': {
                'info': 'details',
                'tmdb_type': 'tv',
                'tmdb_id': tmdb_id,
                'season': try_int(season),
                'episode': try_int(episode),
            }
        }

    def get_items(self, tmdb_id, episodes, **kwargs):
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('episode', 'container')
        return [
            self.get_item_details(tmdb_id, *i.split('x'))
            for i in episodes.split('/')
        ]
