from tmdbhelper.lib.items.directories.trakt.mapper_standard import MediaItemMapper
from tmdbhelper.lib.items.directories.trakt.mapper_basic import NullItemMapper
from jurialmunkey.ftools import cached_property


class MediaMDbListItemMapper(MediaItemMapper):

    tmdb_type = ''
    mediatype = ''

    @cached_property
    def label(self):
        return self.meta.get('title') or ''

    @cached_property
    def tmdb_id(self):
        return self.unique_ids.get('tmdb')

    infolabels_map = {
        'release_year': 'year',
        'description': 'plot',
        'season': 'season',
        'episode': 'episode',
    }
    infoproperties_map = {
        'rank': 'rank',
        'language': 'language',
        'spoken_language': 'spoken_language',
    }

    def get_unique_ids(self):
        unique_ids = {
            'tmdb': self.meta['id'],
            'imdb': self.meta.get('imdb_id'),
        }
        return unique_ids

    def get_params(self):
        params = {
            'info': 'details',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': self.tmdb_type,
        }
        return params


class MovieMDbListItemMapper(MediaMDbListItemMapper):
    tmdb_type = 'movie'
    mediatype = 'movie'


class TVShowMDbListItemMapper(MediaMDbListItemMapper):
    tmdb_type = 'tv'
    mediatype = 'tvshow'


class SeasonMDbListItemMapper(MediaMDbListItemMapper):
    tmdb_type = 'tv'
    mediatype = 'season'


class EpisodeMDbListItemMapper(MediaMDbListItemMapper):
    tmdb_type = 'tv'
    mediatype = 'episode'


def FactoryMDbListItemMapper(meta, add_infoproperties=None):
    routes = {
        'movie': MovieMDbListItemMapper,
        'show': TVShowMDbListItemMapper,
        'season': SeasonMDbListItemMapper,
        'episode': EpisodeMDbListItemMapper,
    }

    try:
        mediatype = meta['mediatype']
        return routes[mediatype](meta, add_infoproperties)
    except KeyError:
        return NullItemMapper()
