from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.mappings import ItemMapper


class EpisodeGroup(BaseItem):
    table = 'episode_groups'
    tmdb_type = 'episode_group'
    ftv_id = None

    @cached_property
    def tvshow_tmdb_id(self):
        rows = self.get_cached_list_values(self.table, ('tvshow_id', ), (self.tmdb_id, ), 'tmdb_id=?')
        return try_int(rows[0]['tvshow_id'].split('.')[-1]) if rows else None

    @property
    def tvshow_id(self):
        return self.get_base_id('tv', self.tvshow_tmdb_id)

    @property
    def data_cond(self):
        if not self.tmdb_id or not self.tvshow_tmdb_id:
            return False
        return bool(self.get_cached_list_values(
            self.table, ('tmdb_id', ), (self.tmdb_id, self.tvshow_id), 'tmdb_id=? AND tvshow_id=?'))

    @cached_property
    def item_mapper(self):
        return ItemMapper(self.language, self.tvshow_tmdb_id)

    @property
    def online_data_args(self):
        return ('tv', 'episode_group', self.tmdb_id)

    @property
    def online_data_kwgs(self):
        return {'language': self.language}

    @cached_property
    def online_data(self):
        data = super().online_data
        if not isinstance(data, dict) or data.get('id') != self.tmdb_id or not isinstance(data.get('groups'), list):
            return
        return data

    @staticmethod
    def set_unaired_expiry(*args, **kwargs):
        return

    @property
    def is_translation(self):
        return False

    def get_cached_data_table(self):
        return (
            f'baseitem INNER JOIN {self.table} ON {self.table}.id=baseitem.id '
            f'INNER JOIN tvshow ON tvshow.id={self.table}.tvshow_id'
        )

    @property
    def cached_data_table(self):
        return self.get_cached_data_table()

    def get_cached_data_keys(self):
        return (*super().cached_data_keys, 'tvshow.tmdb_id AS tvshow_tmdb_id')

    @property
    def cached_data_keys(self):
        return self.get_cached_data_keys()

    @property
    def cached_data_conditions(self):
        return f'{super().cached_data_conditions} AND {self.table}.tvshow_id=?'

    @property
    def cached_data_values(self):
        return (*super().cached_data_values, self.tvshow_id)

    @cached_property
    def db_table_caches(self):
        return tuple(self.return_basemeta_db(route) for route in (
            'base', 'season', 'episode', 'art', 'custom',
            'episode_group_seasons', 'episode_group_season_episodes',
        ))

    def set_cached_data(self, *args, **kwargs):
        self.return_basemeta_db('episode_group_seasons').delete_cached_data()
        super().set_cached_data(*args, **kwargs)

    def get_data(self):
        data = super().get_data()
        if data:
            return data
        cache_refresh = self.cache_refresh
        self.cache_refresh = 'never'
        try:
            return self.get_cached_data()
        finally:
            self.cache_refresh = cache_refresh
