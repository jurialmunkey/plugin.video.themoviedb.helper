from tmdbhelper.lib.items.container import ContainerDirectory
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, ADDONPATH
from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
import xbmcvfs


class ItemViews:

    item_icon_location = ''
    item_icon_default = f'{ADDONPATH}/resources/icons/themoviedb/folder.png'
    item_mediatype = ''

    def __init__(self, name, id, **kwargs):
        self.label = name
        self.tmdb_id = id

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
    def infoproperties(self):
        return {}

    @cached_property
    def unique_ids(self):
        return {'tmdb': self.tmdb_id}

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
            'infoproperties': self.infoproperties,
            'art': self.art,
            'params': self.params,
            'unique_ids': self.unique_ids
        }


"""
GENRES
"""


class ItemGenres(ItemViews):

    item_icon_location = get_setting('genre_icon_location', 'str')
    item_icon_default = f'{ADDONPATH}/resources/icons/themoviedb/genre.png'
    item_mediatype = 'genre'

    def __init__(self, label, tmdb_id, tmdb_type):
        self.label = label
        self.tmdb_id = tmdb_id
        self.tmdb_type = tmdb_type

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
        items = self.query_database.get_genres(tmdb_type)
        items = [ItemGenres(name, tmdb_id, tmdb_type).item for name, tmdb_id in items.items()]
        self.kodi_db = None
        self.container_content = 'genres'
        self.plugin_category = get_localized(135)  # convert_type(tmdb_type, 'plural')
        return items


"""
Studios
"""


class ItemStudios(ItemViews):

    item_mediatype = 'studio'
    tmdb_type = 'movie'

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
    def get_items(self, limit=250, page=1, **kwargs):
        items = self.query_database.get_studios(limit=int(limit), page=int(page))
        items = [ItemStudios(**i).item for i in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'studios'
        return items


"""
Networks
"""


class ItemNetworks(ItemViews):
    item_mediatype = 'studio'
    tmdb_type = 'tv'

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
    def get_items(self, limit=250, page=1, **kwargs):
        items = self.query_database.get_networks(limit=int(limit), page=int(page))
        items = [ItemNetworks(**i).item for i in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'studios'
        return items


"""
Keywords
"""


class ItemKeywords(ItemViews):

    item_mediatype = 'tag'
    tmdb_type = 'movie'

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
    def get_items(self, limit=250, page=1, **kwargs):
        items = self.query_database.get_keywords(limit=int(limit), page=int(page))
        items = [ItemKeywords(**item).item for item in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'tags'
        return items


"""
Collections
"""


class ItemCollections(ItemViews):

    item_mediatype = 'set'
    tmdb_type = 'collection'

    @cached_property
    def params(self):
        return {
            'info': 'collection',
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'plugin_category': self.label,
        }


class ListCollections(ContainerDirectory):
    def get_items(self, limit=20, page=1, **kwargs):
        items = self.query_database.get_collections(limit=int(limit), page=int(page))
        items = [ItemCollections(**i).item for i in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'sets'
        return items


"""
Movies
"""


class ItemMovies(ItemViews):

    item_mediatype = 'movie'
    tmdb_type = 'movie'

    def __init__(self, original_title, id, popularity, **kwargs):
        self.label = original_title
        self.popularity = popularity
        self.tmdb_id = id

    @cached_property
    def infoproperties(self):
        return {
            'popularity': self.popularity,
        }

    @cached_property
    def params(self):
        return {
            'info': 'details',
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'plugin_category': self.label,
        }


class ListMovies(ContainerDirectory):
    def get_items(self, limit=20, page=1, **kwargs):
        items = self.query_database.get_movies(limit=int(limit), page=int(page))
        items = [ItemMovies(**i).item for i in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'movies'
        return items


"""
Tvshows
"""


class ItemTvshows(ItemViews):

    item_mediatype = 'tvshow'
    tmdb_type = 'tvshow'

    def __init__(self, original_name, id, popularity, **kwargs):
        self.label = original_name
        self.popularity = popularity
        self.tmdb_id = id

    @cached_property
    def infoproperties(self):
        return {
            'popularity': self.popularity,
        }

    @cached_property
    def params(self):
        return {
            'info': 'details',
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'plugin_category': self.label,
        }


class ListTvshows(ContainerDirectory):
    def get_items(self, limit=20, page=1, **kwargs):
        items = self.query_database.get_tvshows(limit=int(limit), page=int(page))
        items = [ItemTvshows(**i).item for i in items]
        items.append({'next_page': int(page) + 1})
        self.kodi_db = None
        self.container_content = 'tvshows'
        return items


"""
PROVIDERS
"""


class ItemProviders(ItemViews):
    item_icon_location = get_setting('provider_icon_location', 'str')
    item_mediatype = 'provider'

    def __init__(self, provider_name, provider_id, tmdb_type, iso_country, logo_path, **kwargs):
        self.label = provider_name
        self.tmdb_id = provider_id
        self.tmdb_type = tmdb_type
        self.iso_country = iso_country
        self.logo_path = logo_path

    @cached_property
    def item_icon_default(self):
        return TMDbImagePath().get_imagepath_origin(self.logo_path)

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
        items = self.query_database.get_watch_providers(tmdb_type, self.tmdb_api.iso_country, allowlist_only=True)
        items = [ItemProviders(**i).item for i in items]
        self.kodi_db = None
        self.container_content = ''
        self.plugin_category = 'JustWatch'
        return items


"""
Reviews (items only for elsewhere)
"""


class ItemReviews(ItemViews):
    item_mediatype = 'review'
    tmdb_type = ''

    def __init__(self, author, author_details, content, created_at, updated_at, url, id, **kwargs):
        self.label = author
        self.tmdb_id = id
        self.content = content
        self.url = url
        self.author_details = author_details or {}
        self.init_dates('created_at', created_at)
        self.init_dates('updated_at', updated_at)

    def init_dates(self, name, value):
        setattr(self, name, value)
        setattr(self, f'{name}_date', self.slice_datetime(value, None, 10))
        setattr(self, f'{name}_time', self.slice_datetime(value, 11, 16))

    @staticmethod
    def slice_datetime(datetime, start=None, stop=None):
        return datetime[slice(start, stop)] if datetime else ''

    @cached_property
    def icon(self):
        return TMDbImagePath().get_imagepath_origin(self.author_details.get('avatar_path') or '')

    @cached_property
    def ratings(self):
        return {
            'rating': float(self.author_details['rating'])
        } if self.author_details.get('rating') else {}

    @cached_property
    def infolabels(self):
        infolabels = {
            'title': self.label,
            'plot': self.content,
            'premiered': self.updated_at_date
        }
        infolabels.update(self.ratings)
        return infolabels

    @cached_property
    def infoproperties(self):
        from tmdbhelper.lib.items.database.mappings import ItemMapperMethods
        infoproperties = {
            'name': self.author_details.get('name') or '',
            'username': self.author_details.get('username') or '',
            'url': self.url,
            'created_at.time': self.created_at_time,
            'updated_at.time': self.updated_at_time,
            'content': self.content,
            'tmdb_id': self.tmdb_id,
        }
        infoproperties.update(ItemMapperMethods.get_custom_date(self.created_at_date, name='created_at'))
        infoproperties.update(ItemMapperMethods.get_custom_date(self.updated_at_date, name='updated_at'))
        return infoproperties

    @cached_property
    def params(self):
        return {}
