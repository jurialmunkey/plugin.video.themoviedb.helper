from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode import Episode


class EpisodeMediaList(MediaList):
    table = 'episode'
    cached_data_base_conditions = 'episode.season_id=?'
    cached_data_check_key = 'episode'
    item_mediatype = 'episode'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    sort_by_fallback = 'episode.episode'
    order_by_direction_fallback = 'ASC'

    @property
    def keys(self):
        return Episode.get_keys(self)

    @property
    def cached_data_keys(self):
        return Episode.get_cached_data_keys(self)

    @property
    def cached_data_table(self):
        return Episode.get_cached_data_table(self)

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

    @cached_property
    def parent_precache_tvshow(self):
        return self.get_parent_data('tvshow')

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if not self.parent_precache_tvshow:  # Do some precaching here as we need this data to join
            return False
        return True

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
