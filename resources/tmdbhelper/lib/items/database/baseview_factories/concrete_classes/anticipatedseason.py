from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.seasons import SeasonMediaList
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.flatseasons import FlatSeasonMediaListMixin
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH
from jurialmunkey.ftools import cached_property


class AnticipatedSeasonMediaListMixin(FlatSeasonMediaListMixin):
    @cached_property
    def parent_precache_season(self):
        return self.get_parent_precache_season()

    def get_parent_precache_season(self):
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


class AnticipatedSeasonMediaList(AnticipatedSeasonMediaListMixin, SeasonMediaList):
    table = 'season'
    item_specialseason = get_localized(32206)
    cached_data_base_conditions = 'season.tvshow_id=? AND totalepisodes>0'
    order_by = 'season DESC'
    limit = 1

    def map_label(self, i):
        return self.item_specialseason

    def map_item_infolabels(self, i):
        infolabels = super().map_item_infolabels(i)
        infolabels['title'] = self.item_specialseason
        infolabels['episode'] = i['totalepisodes']
        infolabels['season'] = -1
        return infolabels

    def map_item_infoproperties(self, i):
        return {
            'totalepisodes': i['totalepisodes'],
            'unwatchedepisodes': i['totalepisodes'],
            'specialseason': self.item_specialseason,
            'IsSpecial': 'true'
        }

    @property
    def cached_data_keys(self):
        return self.get_cached_data_keys()

    def map_item_art(self, i):
        map_item_art = self.parent_item_data['art']
        map_item_art['thumb'] = f'{ADDONPATH}/resources/icons/themoviedb/episodes.png'
        map_item_art['poster'] = map_item_art['thumb']
        return map_item_art

    def get_cached_data_keys(self):
        """ SELECT """

        cached_data_keys = [f'{self.table}.{k}' for k in self.keys if k != 'plot']
        cached_data_keys.extend([
            'tvshow.title AS tvshowtitle',
            'tvshow.tagline as tagline',
            'ifnull(season.plot, tvshow.plot) as plot',
            (
                '(    SELECT COUNT(episode.season_id) '
                '     FROM episode WHERE episode.season_id=season.id '
                '                    AND episode.premiered>DATE("now")'
                '     GROUP BY episode.season_id'
                ') as totalepisodes'
            )
        ])
        return tuple(cached_data_keys)

    def map_item_params(self, i):
        return {
            'info': 'anticipated_episodes',
            'tmdb_type': 'tv',
            'tmdb_id': self.tmdb_id,
        }


class Tvshow(AnticipatedSeasonMediaList):
    pass
