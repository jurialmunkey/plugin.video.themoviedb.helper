from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.tvshow import Tvshow
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.consts import SHORTER_EXPIRY


class Season(Tvshow):
    table = 'season'
    cached_data_check_key = 'tvshow_id'
    expiry_time = SHORTER_EXPIRY  # Refresh weekly in case of new episodes

    @property
    def online_data_kwgs(self):
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow}

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if self.season is None:
            return False
        if int(self.season) < 0:
            return False
        return True

    @property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def tvshow_id(self):
        return self.get_base_id(self.tmdb_type, self.tmdb_id)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season)

    @property
    def cached_data_table(self):
        """ FROM """
        return (
            f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id'
            ' LEFT JOIN tvshow ON tvshow.id = season.tvshow_id'
        )

    @property
    def cached_data_keys(self):
        """ SELECT """
        additional_keys = ['tvshow.title AS tvshowtitle', 'tvshow.tagline as tagline']
        return tuple([f'{self.table}.{k}' for k in self.keys] + additional_keys)

    def db_baseitem_cache_get_parent_data(self):
        base_dbc = Tvshow()
        base_dbc.common_apis = self.common_apis
        base_dbc.mediatype = 'tvshow'
        base_dbc.tmdb_id = self.tmdb_id
        return base_dbc.data

    @cached_property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('episode'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('art'),
        )
