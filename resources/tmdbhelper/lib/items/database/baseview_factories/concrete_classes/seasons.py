from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.season import Season


class SeasonMediaList(MediaList):
    table = 'season'
    cached_data_base_conditions = 'season.tvshow_id=?'
    cached_data_check_key = 'season'
    item_mediatype = 'season'
    item_tmdb_type = 'tv'
    item_label_key = 'title'
    order_by = 'season=0, season ASC'

    @property
    def keys(self):
        return Season.get_keys(self)

    @property
    def cached_data_keys(self):
        return Season.get_cached_data_keys(self)

    @property
    def cached_data_table(self):
        return Season.get_cached_data_table(self)

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
