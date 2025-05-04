from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class EpisodeMediaList(MediaList):
    cached_data_table = table = 'episode'
    cached_data_conditions_base = 'season_id=? ORDER BY episode ASC'
    cached_data_check_key = 'episode'
    keys = ('episode', 'year', 'plot', 'title', 'premiered', 'rating', 'votes')
    item_mediatype = 'episode'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    def map_item_infolabels(self, i):
        infolabels = super().map_item_infolabels(i)
        infolabels['season'] = self.season
        return infolabels

    @cached_property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def cached_data_values(self):
        return (self.item_id, )

    def map_item_unique_ids(self, i):
        return {
            'tmdb': self.tmdb_id,
            'tvshow.tmdb': self.tmdb_id
        }

    def map_item_params(self, i):
        return {
            'info': 'details',
            'tmdb_type': self.item_tmdb_type,
            'tmdb_id': self.tmdb_id,
            'season': self.season,
            'episode': i['episode']
        }


class Season(EpisodeMediaList):
    pass
