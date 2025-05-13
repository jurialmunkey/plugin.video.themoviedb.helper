from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.seasons import SeasonMediaList
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX
from tmdbhelper.lib.files.ftools import cached_property


class FlatSeasonMediaList(MediaList):
    table = 'episode'
    cached_data_conditions_base = 'episode.tvshow_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? ORDER BY season=0, season ASC, episode ASC'
    cached_data_check_key = 'episode'
    keys = ()
    item_mediatype = 'episode'
    item_tmdb_type = 'tv'
    item_label_key = 'title'

    filter_key_map = {
        'season': 'season',
        'episode': 'episode',
        'year': 'year',
        'title': 'title',
        'votes': 'votes',
        'premiered': 'premiered',
        'rating': 'rating',
    }

    @cached_property
    def parent_precache_tvshow(self):
        return self.get_parent_data('tvshow')

    @cached_property
    def parent_season_media_list(self):
        season_media_list = SeasonMediaList()
        season_media_list.mediatype = 'tvshow'
        season_media_list.tmdb_id = self.tmdb_id
        season_media_list.tmdb_type = self.tmdb_type
        return season_media_list.data

    @cached_property
    def parent_precache_seasons(self):
        if not self.parent_season_media_list:
            return []
        return [
            self.get_parent_data('season', season['infolabels']['season'])
            for season in self.parent_season_media_list
            if season and 'infolabels' in season and season['infolabels'].get('season')
        ]

    def get_parent_data(self, mediatype, season=None, episode=None):
        try:
            base_dbc = BaseItemFactory(mediatype)
            base_dbc.mediatype = mediatype
            base_dbc.tmdb_id = self.tmdb_id
            base_dbc.tmdb_type = self.tmdb_type
            base_dbc.season = season
            base_dbc.episode = episode
            base_dbc.common_apis = self.common_apis
            base_dbc.connection = self.connection
            base_dbc.cache = self.cache
        except (TypeError, KeyError, IndexError, ValueError):
            return
        return base_dbc.data

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if not self.parent_precache_tvshow:  # Do some precaching here as we need this data to join
            return False
        if not self.parent_precache_seasons:  # Do some precaching here as we need this data to join
            return
        return True

    @property
    def cached_data_table(self):
        return (
            'episode'
            ' INNER JOIN season ON episode.season_id = season.id'
            ' INNER JOIN baseitem ON episode.tvshow_id = baseitem.id'
        )

    @property
    def cached_data_keys(self):
        return (
            'episode', 'episode.year as year', 'episode.plot as plot', 'episode.title as title',
            'episode.premiered as premiered', 'episode.rating as rating', 'episode.votes as votes',
            'season.season as season'
        )

    @property
    def cached_data_values(self):
        return (self.item_id, self.current_time, DATALEVEL_MAX)

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
            'season': i['season'],
            'episode': i['episode']
        }


class Tvshow(FlatSeasonMediaList):
    pass
