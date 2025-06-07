from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from tmdbhelper.lib.files.ftools import cached_property


class MediaItemMapper(ItemMapper):

    tmdb_type = ''
    mediatype = ''

    @cached_property
    def label(self):
        return self.meta.get('title') or ''

    @cached_property
    def tmdb_id(self):
        return self.unique_ids['tmdb']

    infolabels_map = {
        'year': 'year',
    }

    def get_infolabels(self):
        infolabels = {
            self.infolabels_map[k]: v
            for k, v in self.meta.items()
            if k in self.infolabels_map
        }
        infolabels['mediatype'] = self.mediatype
        return infolabels

    infoproperties_map = {
        'watchers': 'watchers',
        'watcher_count': 'watchers',
        'play_count': 'plays',
        'collected_count': 'collectors',
        'list_count': 'lists',
    }

    def get_infoproperties(self):
        infoproperties = {
            self.infoproperties_map[k]: v
            for k, v in self.meta.items()
            if k in self.infoproperties_map
        }
        infoproperties.update({k: v for k, v in (self.add_infoproperties or ())})
        infoproperties['tmdb_type'] = self.tmdb_type
        infoproperties['tmdb_id'] = self.tmdb_id
        return infoproperties

    def get_unique_ids(self):
        unique_ids = {}
        unique_ids.update(self.meta.get('ids') or {})
        return unique_ids

    def get_params(self):
        params = {
            'info': 'details',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': self.tmdb_type,
        }
        return params


class MovieItemMapper(MediaItemMapper):
    tmdb_type = 'movie'
    mediatype = 'movie'


class TVShowItemMapper(MediaItemMapper):
    tmdb_type = 'tv'
    mediatype = 'tvshow'


def FactoryItemMapper(meta, add_infoproperties=None, trakt_type=None, sub_type=False):
    routes = {
        'movie': MovieItemMapper,
        'show': TVShowItemMapper,
    }

    try:
        trakt_type = trakt_type or meta['type']
        meta.update(meta.pop(trakt_type, {})) if sub_type else None
        return routes[trakt_type](meta, add_infoproperties)
    except KeyError:
        return ItemMapper()
