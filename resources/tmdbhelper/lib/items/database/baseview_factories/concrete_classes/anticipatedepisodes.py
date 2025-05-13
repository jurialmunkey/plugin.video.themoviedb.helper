from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.seasons import SeasonMediaList
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.flatseasons import FlatSeasonMediaList
from tmdbhelper.lib.files.ftools import cached_property


class AnticipatedEpisodeMediaList(FlatSeasonMediaList):
    cached_data_conditions_base = 'episode.tvshow_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? AND episode.premiered>DATE("now") AND season.season>0 ORDER BY season ASC, episode ASC'

    @cached_property
    def parent_precache_season(self):
        if not self.parent_season_media_list:
            return []
        season_numbers = [
            season['infolabels']['season']
            for season in self.parent_season_media_list
            if season and 'infolabels' in season and season['infolabels'].get('season')
        ]
        return self.get_parent_data('season', max(season_numbers), cache_refresh='basic')

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if not self.parent_precache_tvshow:  # Do some precaching here as we need this data to join
            return False
        if not self.parent_precache_season:  # Do some precaching here as we need this data to join
            return
        return True


class Tvshow(AnticipatedEpisodeMediaList):
    pass
