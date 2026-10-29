from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.flatseasons import FlatSeasonMediaList


class Tvshow(FlatSeasonMediaList):
    """Retrieve a show's episodes within the requested TMDb calendar dates."""
    order_by = 'episode.premiered ASC, season.season ASC, episode.episode ASC'
    cached_data_check_key = 'premiered'

    @property
    def cached_data_base_conditions(self):
        return (
            f'{super().cached_data_base_conditions} '
            'AND episode.premiered>=? AND episode.premiered<?')

    @property
    def cached_data_values(self):
        return (*super().cached_data_values, self.start_date, self.end_date)

    @cached_property
    def parent_precache_seasons(self):
        return self.get_parent_precache_seasons()

    def get_parent_precache_seasons(self):
        # Include specials, and skip seasons whose premiere is after this range.
        return [
            self.get_parent_data('season', item['infolabels']['season'], cache_refresh='basic')
            for item in self.parent_season_media_list or []
            if not item['infolabels'].get('premiered') or item['infolabels']['premiered'] < self.end_date
        ]

    def map_item_infolabels(self, item):
        labels = super().map_item_infolabels(item)
        labels['tvshowtitle'] = self.parent_precache_tvshow['infolabels']['title']
        return labels
