from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.season import Season
from tmdbhelper.lib.files.ftools import cached_property


class Episode(Season):
    table = 'episode'
    ftv_type = None

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if self.season is None:
            return False
        if int(self.season) < 0:
            return False
        if not self.episode:
            return False
        return True

    @property
    def online_data_cond(self):
        if not self.data_cond:
            return False
        if not self.parent_item_data:
            return False
        return True

    @cached_property
    def parent_item_data(self):
        try:
            base_dbc = Season()
            base_dbc.mediatype = 'season'
            base_dbc.tmdb_type = 'tv'
            base_dbc.tmdb_id = self.tmdb_id
            base_dbc.season = self.season
            base_dbc.common_apis = self.common_apis
            base_dbc.cache = self.cache
        except (TypeError, KeyError, IndexError, ValueError):
            return
        return base_dbc.data

    @property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)

    @property
    def season_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)

    @property
    def online_data_args(self):
        return (self.tmdb_type, self.tmdb_id, 'season', self.season, 'episode', self.episode)

    @property
    def online_data_kwgs(self):
        if self.cache_refresh == 'basic':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_simple}
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow}

    @cached_property
    def online_data(self):
        """ cache online data from func to property """
        if not self.online_data_cond:
            return
        # kodi_log(f'SYNC CACHE: {self.online_data_args}', 2)
        tmdb_data = self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

        trakt_id = self.common_apis.trakt_api.get_id(self.tmdb_id, 'tmdb', 'show', 'trakt')
        if not trakt_id:
            return tmdb_data

        trakt_data = self.common_apis.trakt_api.get_request_sc('shows', trakt_id, 'seasons', self.season, 'episodes', self.episode, extended='full')
        if not trakt_data:
            return tmdb_data

        trakt_data.update(tmdb_data)
        return trakt_data

    @property
    def cached_data_table(self):
        return self.get_cached_data_table()

    @property
    def cached_data_keys(self):
        return self.get_cached_data_keys()

    def get_cached_data_table(self):
        """ FROM """
        return (
            f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id '
            'LEFT JOIN season ON season.id = episode.season_id '
            'LEFT JOIN tvshow ON tvshow.id = episode.tvshow_id '
        )

    def get_cached_data_keys(self):
        """ SELECT """
        additional_keys = ['tvshow.title AS tvshowtitle', 'season.season AS season', 'tvshow.tagline as tagline']
        return tuple([f'{self.table}.{k}' for k in self.keys] + additional_keys)

    @property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('art'),
        )
