from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper


class EpisodeGroupItemMapper(ItemMapper):

    @cached_property
    def tmdb_id(self):
        return self.meta['tmdb_id']

    @cached_property
    def group(self):
        return self.meta['group']

    @cached_property
    def label(self):
        return self.group['title'] or ''

    def get_infolabels(self):
        return {'mediatype': 'tvshow', 'title': self.label, 'plot': self.group['plot']}

    def get_infoproperties(self):
        return {'label_override': self.label}

    def get_unique_ids(self):
        return {'tmdb': self.tmdb_id, 'group_tmdb': self.group['tmdb_id']}

    def get_params(self):
        return {
            'info': 'episode_group_seasons', 'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id, 'group_id': self.group['tmdb_id'],
        }

    def get_item(self):
        item = super().get_item()
        # A blank group plot should clear the parent show's plot during detail merging.
        item['infolabels']['plot'] = self.group['plot']
        item['is_folder'] = True
        return item


class EpisodeGroupSeasonItemMapper(EpisodeGroupItemMapper):

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties.update({
            key: self.group[key]
            for key in ('totalepisodes', 'airedepisodes', 'watchedepisodes')
        })
        infoproperties['group_season'] = self.group['ordering']
        return infoproperties

    def get_unique_ids(self):
        unique_ids = super().get_unique_ids()
        unique_ids.update({
            'tvshow.tmdb': self.tmdb_id,
            'group_tmdb': self.group['group_id'],
            'season_group_tmdb': self.group['tmdb_id'],
        })
        return unique_ids

    def get_params(self):
        params = super().get_params()
        params.update({
            'info': 'episode_group_season_episodes',
            'group_id': self.group['group_id'],
            'season_group_id': self.group['tmdb_id'],
        })
        return params


class EpisodeGroupEpisodeItemMapper(EpisodeGroupItemMapper):

    def get_infolabels(self):
        infolabels = super().get_infolabels()
        infolabels.update({
            'mediatype': 'episode',
            'season': self.group['season'], 'episode': self.group['episode'],
        })
        return infolabels

    def get_infoproperties(self):
        infoproperties = super().get_infoproperties()
        infoproperties.update({
            'group_season': self.group['group_ordering'],
            'group_episode': self.group['ordering'],
        })
        return infoproperties

    def get_unique_ids(self):
        return {
            'tmdb': self.group['tmdb_id'], 'tvshow.tmdb': self.tmdb_id,
            'group_tmdb': self.group['group_id'],
            'season_group_tmdb': self.group['season_group_id'],
        }

    def get_params(self):
        return {
            'info': 'details', 'tmdb_type': 'tv', 'tmdb_id': self.tmdb_id,
            'season': self.group['season'], 'episode': self.group['episode'],
        }
