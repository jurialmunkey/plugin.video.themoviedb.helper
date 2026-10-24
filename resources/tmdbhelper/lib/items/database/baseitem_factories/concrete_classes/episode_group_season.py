from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode_group import EpisodeGroup
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.episode_groups import EpisodeGroupSeasons


class EpisodeGroupSeason(EpisodeGroup):
    table = 'episode_group_seasons'
    tmdb_type = 'episode_group_season'
    online_data_cond = False
    db_table_caches = ()

    @cached_property
    def group_id(self):
        rows = self.get_cached_list_values(self.table, ('group_id', ), (self.tmdb_id, ), 'tmdb_id=?')
        return rows[0]['group_id'] if rows else None

    @cached_property
    def parent_item_data(self):
        database_obj = BaseItemFactory('episode_group', common_apis=self.common_apis)
        database_obj.tmdb_id = self.group_id
        database_obj.tvshow_tmdb_id = self.tvshow_tmdb_id
        database_obj.cache = self.cache
        database_obj.connection = self.connection
        database_obj.cache_refresh = self.cache_refresh
        return database_obj.data

    @property
    def data_cond(self):
        return bool(self.tmdb_id and self.group_id and self.parent_item_data and super().data_cond)

    @property
    def cached_data_conditions(self):
        return f'{super().cached_data_conditions} AND {self.table}.group_id=?'

    @property
    def cached_data_values(self):
        return (*super().cached_data_values, self.group_id)

    def get_cached_data_keys(self):
        return (*super().get_cached_data_keys(), *EpisodeGroupSeasons.get_count_keys())
