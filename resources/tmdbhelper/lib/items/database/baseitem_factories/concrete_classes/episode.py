from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.season import Season
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.tvshow import Tvshow
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.locker import mutexlock


class Episode(Season):
    table = 'episode'
    ftv_type = None

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if self.season in (None, ''):
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
        return self.get_parent_item_data()

    @property
    def mutex_lockname(self):
        return f'Database.ItemDetails.tv.{self.tmdb_id}.{self.season}.lockfile'

    @mutexlock
    def get_parent_item_data(self):
        try:
            base_dbc = Season()
            base_dbc.mediatype = 'season'
            base_dbc.tmdb_type = 'tv'
            base_dbc.tmdb_id = self.tmdb_id
            base_dbc.season = self.season
            base_dbc.common_apis = self.common_apis
            base_dbc.cache = self.cache
            base_dbc.cache_refresh = self.cache_refresh
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
        if self.cache_refresh == 'langs':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_translation}
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response}

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
            ' LEFT JOIN season ON season.id = episode.season_id'
            ' LEFT JOIN tvshow ON tvshow.id = episode.tvshow_id'
            ' LEFT JOIN episode next_aired ON next_aired.id = tvshow.next_episode_to_air_id'
            ' LEFT JOIN episode last_aired ON last_aired.id = tvshow.last_episode_to_air_id'
        )

    def get_cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys if k != 'status']
        cached_data_keys.extend([
            'episode.status AS episode_type',
            'tvshow.title AS tvshowtitle',
            'tvshow.originaltitle AS tvshow_originaltitle',
            'tvshow.tagline AS tagline',
            'tvshow.status AS status',
            'tvshow.premiered AS tvshow_premiered',
            'tvshow.year AS tvshow_year',
            'season.season AS season',
        ])
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('next_aired'))
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('last_aired'))
        return tuple(cached_data_keys)

    @property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('service'),
            self.return_basemeta_db('provider'),
            self.return_basemeta_db('person'),
            self.return_basemeta_db('castmember'),
            self.return_basemeta_db('crewmember'),
            self.return_basemeta_db('translation'),
            self.return_basemeta_db('unique_id'),
            self.return_basemeta_db('custom'),
            self.return_basemeta_db('art'),
        )
