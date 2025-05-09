from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class SeasonMediaList(MediaList):
    table = 'season'
    cached_data_conditions_base = 'tvshow_id=? ORDER BY season=0, season ASC'
    cached_data_check_key = 'season'
    keys = ('season', 'year', 'plot', 'title', 'premiered', 'rating')
    item_mediatype = 'season'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    cached_data_table = 'season INNER JOIN tvshow ON tvshow.id = season.tvshow_id'
    cached_data_keys = ('season', 'season.year as year', 'ifnull(season.plot, tvshow.plot) as plot', 'season.title as title', 'season.premiered as premiered', 'season.rating as rating', 'tvshow.title as tvshowtitle')

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
