from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.basemedia import MediaItem
from jurialmunkey.ftools import cached_property


class Tvshow(MediaItem):
    table = 'tvshow'
    tmdb_type = 'tv'
    ftv_type = 'tv'

    @property
    def cached_data_table(self):
        """ FROM """
        return (
            f'baseitem LEFT JOIN {self.table} ON {self.table}.id = baseitem.id '
            f'LEFT JOIN episode next_aired ON next_aired.id = {self.table}.next_episode_to_air_id '
            f'LEFT JOIN episode last_aired ON last_aired.id = {self.table}.last_episode_to_air_id '
        )

    @staticmethod
    def cached_data_keys_episode_to_air(prefix='next_aired'):
        return [
            f'{prefix}.id AS {prefix}_id',
            f'{prefix}.episode AS {prefix}_episode',
            f'{prefix}.year AS {prefix}_year',
            f'{prefix}.premiered AS {prefix}_premiered',
            f'{prefix}.duration AS {prefix}_duration',  # TODO: FORMAT THESE TOO!
            f'{prefix}.rating AS {prefix}_rating',
            f'{prefix}.votes AS {prefix}_votes',
            f'{prefix}.popularity AS {prefix}_popularity',
            f'{prefix}.title AS {prefix}_title',
            f'{prefix}.plot AS {prefix}_plot',
        ]

    @property
    def cached_data_keys(self):
        """ SELECT """
        cached_data_keys = [f'{self.table}.{k}' for k in self.keys if k != 'duration']
        cached_data_keys.extend([(
            'ifnull('
            '(    SELECT CAST(AVG(episode.duration) as INTEGER) '
            '     FROM episode WHERE episode.tvshow_id=tvshow.id '
            '                    AND episode.premiered<=DATE("now")'
            '                    AND episode.status!="special"'
            '     GROUP BY episode.tvshow_id'
            '), tvshow.duration) as duration'
        )])
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('next_aired'))
        cached_data_keys.extend(Tvshow.cached_data_keys_episode_to_air('last_aired'))
        return tuple(cached_data_keys)

    @property
    def online_data_kwgs(self):
        if self.cache_refresh == 'basic':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_simple}
        if self.cache_refresh == 'langs':
            return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow_translation}
        return {'append_to_response': self.common_apis.tmdb_api.append_to_response_tvshow}

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
            'basemeta_db_fanart_tv_poster_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_poster_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_poster_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_poster_null_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_fanart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_landscape_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_landscape_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_landscape_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearlogo_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearlogo_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearlogo_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearlogo_null_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_clearart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_banner_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_fanart_tv_poster_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_poster_language_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_poster_english_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_poster_null_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_fanart_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_landscape_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_landscape_language_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_landscape_english_season': self.config_basemeta_db_season,
            'basemeta_db_fanart_tv_banner_season': self.config_basemeta_db_season,

            'basemeta_db_art_poster_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_poster_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_poster_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_poster_null_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_fanart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_landscape_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_landscape_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_landscape_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_clearlogo_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_clearlogo_language_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_clearlogo_english_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_clearlogo_null_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_art_poster_season': self.config_basemeta_db_season,
            'basemeta_db_art_poster_language_season': self.config_basemeta_db_season,
            'basemeta_db_art_poster_english_season': self.config_basemeta_db_season,
            'basemeta_db_art_poster_null_season': self.config_basemeta_db_season,
            'basemeta_db_art_fanart_season': self.config_basemeta_db_season,
            'basemeta_db_art_landscape_season': self.config_basemeta_db_season,
            'basemeta_db_art_landscape_language_season': self.config_basemeta_db_season,
            'basemeta_db_art_landscape_english_season': self.config_basemeta_db_season,
            'basemeta_db_art_clearlogo_season': self.config_basemeta_db_season,
            'basemeta_db_art_clearlogo_language_season': self.config_basemeta_db_season,
            'basemeta_db_art_clearlogo_english_season': self.config_basemeta_db_season,
            'basemeta_db_art_clearlogo_null_season': self.config_basemeta_db_season,

            'basemeta_db_user_art_poster_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_user_art_fanart_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_user_art_landscape_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_user_art_clearlogo_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_user_art_thumb_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_user_art_poster_season': self.config_basemeta_db_season,
            'basemeta_db_user_art_fanart_season': self.config_basemeta_db_season,
            'basemeta_db_user_art_landscape_season': self.config_basemeta_db_season,
            'basemeta_db_user_art_clearlogo_season': self.config_basemeta_db_season,
            'basemeta_db_user_art_thumb_season': self.config_basemeta_db_season,

            'basemeta_db_unique_id_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_unique_id_season': self.config_basemeta_db_season,
            'basemeta_db_custom_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_custom_season': self.config_basemeta_db_season,
            'basemeta_db_translation_tvshow': self.config_basemeta_db_tvshow,
            'basemeta_db_translation_season': self.config_basemeta_db_season,
        }

    @cached_property
    def db_table_caches(self):
        """ Database tables that will have data set as part of cache setter """
        return (
            self.return_basemeta_db('base'),
            self.return_basemeta_db('belongs'),
            self.return_basemeta_db('season'),
            self.return_basemeta_db('episode'),
            self.return_basemeta_db('genre'),
            self.return_basemeta_db('country'),
            self.return_basemeta_db('certification'),
            self.return_basemeta_db('translation'),
            self.return_basemeta_db('video'),
            self.return_basemeta_db('company'),
            self.return_basemeta_db('studio'),
            self.return_basemeta_db('broadcaster'),
            self.return_basemeta_db('network'),
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
