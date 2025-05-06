from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.files.ftools import cached_property


class Tvshow(MediaItem):
    table = 'tvshow'
    tmdb_type = 'tv'
    db_studio_table = 'network'
    ftv_type = 'tv'

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow}

    @cached_property
    def ftv_id(self):
        return self.common_apis.trakt_api.get_id(self.tmdb_id, 'tmdb', 'show', 'tvdb')

    def config_basemeta_db_tvshow(self, database_obj):
        database_obj = self.config_basemeta_db(database_obj)
        database_obj.item_id = self.tvshow_id
        database_obj.parent_id = self.tvshow_id
        database_obj.mediatype = 'tvshow'
        return database_obj

    def config_basemeta_db_season(self, database_obj):
        database_obj = self.config_basemeta_db(database_obj)
        database_obj.item_id = self.season_id
        database_obj.parent_id = self.season_id
        database_obj.mediatype = 'season'
        database_obj.season = self.season
        return database_obj

    @cached_property
    def routes_basemeta_db(self):
        return {
            'basemeta_db_studio': self.config_basemeta_db_studio,
            'basemeta_db_fanart_tv_poster_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_fanart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_landscape_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearlogo_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_banner_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_poster_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_fanart_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_landscape_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_banner_season': self.config_basemeta_db_season,
            'basemeta_db_art_poster_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_fanart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_landscape_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_clearlogo_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_poster_season': self.config_basemeta_db_season,
            'basemeta_db_art_fanart_season': self.config_basemeta_db_season,
            'basemeta_db_art_landscape_season': self.config_basemeta_db_season,
            'basemeta_db_art_clearlogo_season': self.config_basemeta_db_season,
            'basemeta_db_unique_id_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_unique_id_season': self.config_basemeta_db_season,
            'basemeta_db_custom_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_custom_season': self.config_basemeta_db_season,
        }

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('season'),
            self.return_basemeta_db('episode'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
            self.return_basemeta_db('video'),
            self.return_basemeta_db('company'),
            self.return_basemeta_db('studio'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('fanart_tv'),
            self.return_basemeta_db('art'),

        )
