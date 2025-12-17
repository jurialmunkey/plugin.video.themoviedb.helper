from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.tvshow import Tvshow
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.consts import SHORTER_EXPIRY
from tmdbhelper.lib.files.locker import mutexlock


class Season(Tvshow):
    table = 'season'
    cached_data_check_key = 'tvshow_id'
    expiry_time = SHORTER_EXPIRY  # Refresh weekly in case of new episodes
    ftv_type = None

    @property
    def online_data_kwgs(self):
        if self.cache_refresh == 'basic':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_simple}
        if self.cache_refresh == 'langs':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_translation}
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow}

    @property
    def data_cond(self):
        """ Determines if any data is returned """
        if not self.tmdb_id:
            return False
        if self.season in (None, ''):
            return False
        if int(self.season) < 0:
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
        return f'Database.ItemDetails.tv.{self.tmdb_id}.lockfile'

    @mutexlock
    def get_parent_item_data(self):
        try:
            base_dbc = Tvshow()
            base_dbc.mediatype = 'tvshow'
            base_dbc.tmdb_type = 'tv'
            base_dbc.tmdb_id = self.tmdb_id
            base_dbc.common_apis = self.common_apis
            base_dbc.cache = self.cache
            base_dbc.cache_refresh = self.cache_refresh
        except (TypeError, KeyError, IndexError, ValueError):
            return
        return base_dbc.data

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
        return self.get_cached_data_table()

    @property
    def cached_data_keys(self):
        return self.get_cached_data_keys()

    @property
    def cached_data_conditions(self):
        return f'{super().cached_data_conditions}'

    def get_cached_data_table(self):
        """ FROM """
        return (
            f'baseitem INNER JOIN {self.table} ON {self.table}.id = baseitem.id'
            ' LEFT JOIN tvshow ON tvshow.id = season.tvshow_id'
            ' LEFT JOIN episode next_aired ON next_aired.id = tvshow.next_episode_to_air_id'
            ' LEFT JOIN episode last_aired ON last_aired.id = tvshow.last_episode_to_air_id'
        )

    def get_cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys if k not in ('plot', 'status', 'duration')]
        cached_data_keys.extend([
            'tvshow.title AS tvshowtitle',
            'tvshow.tagline as tagline',
            'tvshow.status AS status',
            'ifnull(season.plot, tvshow.plot) as plot',
            (
                '(    SELECT COUNT(episode.season_id) '
                '     FROM episode WHERE episode.season_id=season.id '
                '                    AND episode.premiered<=DATE("now")'
                '     GROUP BY episode.season_id'
                ') as totalepisodes'
            ),
            (
                'ifnull('
                '(    SELECT CAST(AVG(episode.duration) as INTEGER) '
                '     FROM episode WHERE episode.season_id=season.id '
                '                    AND episode.premiered<=DATE("now")'
                '     GROUP BY episode.season_id'
                '), tvshow.duration) as duration'
            )
        ])
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('next_aired'))
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('last_aired'))
        return tuple(cached_data_keys)

    @cached_property
    def db_table_caches(self):
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('episode'),
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
