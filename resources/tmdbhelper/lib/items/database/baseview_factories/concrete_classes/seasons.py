from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class SeasonMediaList(MediaList):
    cached_data_table = table = 'season'
    cached_data_conditions_base = 'tvshow_id=? ORDER BY season=0, season ASC'
    cached_data_check_key = 'season'
    keys = ('season', 'year', 'plot', 'title', 'premiered', 'rating')
    item_mediatype = 'season'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    filter_key_map = {
        'season': 'season',
        'year': 'year',
        'title': 'title',
        'premiered': 'premiered',
        'rating': 'rating',
    }

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
            'info': 'episodes',
            'tmdb_type': self.item_tmdb_type,
            'tmdb_id': self.tmdb_id,
            'season': i['season']
        }


class Tvshow(SeasonMediaList):
    pass
