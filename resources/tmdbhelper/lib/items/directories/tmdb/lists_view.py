from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, ADDONPATH
from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
import xbmcvfs


class ItemViews:

    item_icon_location = ''
    item_icon_default = f'{ADDONPATH}/resources/icons/themoviedb/folder.png'
    item_mediatype = ''

    def __init__(self, label, tmdb_id, tmdb_type):
        self.label = label
        self.tmdb_id = tmdb_id
        self.tmdb_type = tmdb_type

    @cached_property
    def params(self):
        return {}

    @cached_property
    def infolabels(self):
        return {
            'title': self.label,
            'mediatype': self.item_mediatype,
        }

    @cached_property
    def icon(self):
        if not self.item_icon_location:
            return self.item_icon_default
        filepath = xbmcvfs.validatePath(xbmcvfs.translatePath(f'{self.item_icon_location}/{self.tmdb_id}.png'))
        if not xbmcvfs.exists(filepath):
            return self.item_icon_default
        return filepath

    @cached_property
    def art(self):
        return {'icon': self.icon} if self.icon else {}

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'infolabels': self.infolabels,
            'infoproperties': {},
            'art': self.art,
            'params': self.params
        }


"""
GENRES
"""


class ItemGenres(ItemViews):

    item_icon_location = get_setting('genre_icon_location', 'str')
    item_icon_default = f'{ADDONPATH}/resources/icons/themoviedb/genre.png'
    item_mediatype = 'genre'

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_genres': self.tmdb_id,
            'with_id': 'True',
            'plugin_category': self.label,
        }


class ListGenres(ContainerDirectory):
    def get_items(self, tmdb_type, **kwargs):
        items = self.tmdb_api.tmdb_database.get_genres(tmdb_type)
        items = [ItemGenres(name, tmdb_id, tmdb_type).item for name, tmdb_id in items.items()]
        self.kodi_db = None
        self.container_content = 'genres'
        self.plugin_category = get_localized(135)  # convert_type(tmdb_type, 'plural')
        return items


"""
Keywords
"""


class ItemKeywords(ItemViews):

    item_mediatype = 'keyword'

    def __init__(self, meta):
        self.meta = meta
        self.label = self.meta['name']
        self.tmdb_id = self.meta['id']
        self.tmdb_type = 'movie'

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_keywords': self.tmdb_id,
            'with_id': 'True',
            'plugin_category': self.label,
        }


class ListKeywords(ContainerDirectory):
    def get_items(self, **kwargs):
        items = self.tmdb_api.tmdb_database.get_keywords()
        items = [ItemKeywords(i).item for i in items]
        self.kodi_db = None
        self.container_content = ''
        # self.plugin_category = get_localized(135)  # convert_type(tmdb_type, 'plural')
        return items


"""
Networks
"""


class ItemNetworks(ItemViews):

    item_mediatype = 'keyword'

    def __init__(self, meta):
        self.meta = meta
        self.label = self.meta['name']
        self.tmdb_id = self.meta['id']
        self.tmdb_type = 'tv'

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_networks': self.tmdb_id,
            'with_id': 'True',
            'plugin_category': self.label,
        }


class ListNetworks(ContainerDirectory):
    def get_items(self, **kwargs):
        items = self.tmdb_api.tmdb_database.get_networks()
        items = [ItemNetworks(i).item for i in items]
        self.kodi_db = None
        self.container_content = ''
        # self.plugin_category = get_localized(135)  # convert_type(tmdb_type, 'plural')
        return items


"""
Studios
"""


class ItemStudios(ItemViews):

    item_mediatype = 'keyword'

    def __init__(self, meta):
        self.meta = meta
        self.label = self.meta['name']
        self.tmdb_id = self.meta['id']
        self.tmdb_type = 'movie'

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_companies': self.tmdb_id,
            'with_id': 'True',
            'plugin_category': self.label,
        }


class ListStudios(ContainerDirectory):
    def get_items(self, **kwargs):
        items = self.tmdb_api.tmdb_database.get_studios()
        items = [ItemStudios(i).item for i in items]
        self.kodi_db = None
        self.container_content = ''
        # self.plugin_category = get_localized(135)  # convert_type(tmdb_type, 'plural')
        return items


"""
PROVIDERS
"""


class ItemProviders(ItemViews):
    item_icon_location = get_setting('provider_icon_location', 'str')
    item_mediatype = 'provider'

    def __init__(self, meta):
        self.meta = meta
        self.label = self.meta['provider_name']
        self.tmdb_id = self.meta['provider_id']
        self.tmdb_type = self.meta['tmdb_type']
        self.iso_country = self.meta['iso_country']

    @cached_property
    def item_icon_default(self):
        return TMDbImagePath().get_imagepath_origin(self.meta['logo_path'])

    @cached_property
    def params(self):
        return {
            'info': 'discover',
            'tmdb_type': self.tmdb_type,
            'with_watch_providers': self.tmdb_id,
            'watch_region': self.iso_country,
            'with_id': 'True',
            'plugin_category': self.label,
        }


class ListProviders(ContainerDirectory):
    def get_items(self, tmdb_type, **kwargs):
        items = self.tmdb_api.tmdb_database.get_watch_providers(tmdb_type, self.tmdb_api.iso_country, allowlist_only=True)
        items = [ItemProviders(i).item for i in items]
        self.kodi_db = None
        self.container_content = ''
        self.plugin_category = 'JustWatch'
        return items
