from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from jurialmunkey.ftools import cached_property


class MDbListUpNextItemMapper(ItemMapper):

    @cached_property
    def show(self):
        return self.meta.get('show') or {}

    @cached_property
    def episode_data(self):
        return self.meta.get('next_episode') or {}

    @cached_property
    def show_tmdb_id(self):
        return (self.show.get('ids') or {}).get('tmdb')

    @cached_property
    def episode_tmdb_id(self):
        return (self.episode_data.get('ids') or {}).get('tmdb')

    @cached_property
    def label(self):
        return self.episode_data.get('title') or self.show.get('title') or ''

    def get_infolabels(self):
        return {
            'mediatype': 'episode',
            'title': self.episode_data.get('title'),
            'tvshowtitle': self.show.get('title'),
            'season': self.episode_data.get('season'),
            'episode': self.episode_data.get('episode'),
            'premiered': self.episode_data.get('air_date'),
            'year': self.show.get('year'),
        }

    def get_infoproperties(self):
        progress = self.meta.get('progress') or {}
        return {
            'tmdb_type': 'tv',
            'tmdb_id': self.show_tmdb_id,
            'last_watched_at': self.meta.get('last_watched_at'),
            'is_newly_aired': self.meta.get('is_newly_aired'),
            'watched_episode_count': progress.get('watched_episode_count'),
            'total_episode_count': progress.get('total_episode_count'),
        }

    def get_unique_ids(self):
        return {
            'tmdb': self.show_tmdb_id,
            'tvshow.tmdb': self.show_tmdb_id,
            'episode.tmdb': self.episode_tmdb_id,
            'mdblist': (self.show.get('ids') or {}).get('mdblist'),
        }

    def get_art(self):
        return {
            'poster': self.show.get('poster'),
            'thumb': self.episode_data.get('still'),
        }

    def get_params(self):
        return {
            'info': 'details',
            'tmdb_type': 'tv',
            'tmdb_id': self.show_tmdb_id,
            'season': self.episode_data.get('season'),
            'episode': self.episode_data.get('episode'),
        }
