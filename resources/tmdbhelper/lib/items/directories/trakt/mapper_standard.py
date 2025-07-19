from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper, NullItemMapper
from jurialmunkey.ftools import cached_property


class MediaItemMapper(ItemMapper):

    tmdb_type = ''
    mediatype = ''

    def __init__(self, meta, add_infoproperties, sub_type=False):
        self.add_infoproperties = add_infoproperties
        self.meta = meta
        self.meta.update(self.meta.pop(sub_type, {})) if sub_type else None

    @cached_property
    def label(self):
        return self.meta.get('title') or ''

    @cached_property
    def tmdb_id(self):
        return self.unique_ids.get('tmdb')

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
        'rank': 'rank',
        'notes': 'notes',
        'listed_at': 'listed_at',
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


class SeasonItemMapper(MediaItemMapper):
    tmdb_type = 'tv'
    mediatype = 'season'

    @cached_property
    def tvshow_meta(self):
        return self.meta.get('show') or {}

    def get_unique_ids(self):
        unique_ids = {}
        unique_ids = {f'tvshow.{k}': v for k, v in (self.tvshow_meta.get('ids') or {}).items()}
        unique_ids.update(self.meta.get('ids') or {})
        unique_ids['tmdb'] = unique_ids.get('tvshow.tmdb')
        return unique_ids

    def get_infolabels(self):
        infolabels = super().get_infolabels()
        infolabels['tvshowtitle'] = self.tvshow_meta.get('title')
        infolabels['season'] = self.meta.get('number')
        return infolabels


class EpisodeItemMapper(SeasonItemMapper):
    tmdb_type = 'tv'
    mediatype = 'episode'

    def get_infolabels(self):
        infolabels = super().get_infolabels()
        infolabels['tvshowtitle'] = self.tvshow_meta.get('title')
        infolabels['season'] = self.meta.get('season')
        infolabels['episode'] = self.meta.get('number')
        return infolabels


def FactoryItemMapper(meta, add_infoproperties=None, trakt_type=None, sub_type=False):
    routes = {
        'movie': MovieItemMapper,
        'show': TVShowItemMapper,
        'season': SeasonItemMapper,
        'episode': EpisodeItemMapper,
    }

    try:
        trakt_type = trakt_type or meta['type']
        return routes[trakt_type](meta, add_infoproperties, sub_type=trakt_type if sub_type else None)
    except KeyError:
        return NullItemMapper()
