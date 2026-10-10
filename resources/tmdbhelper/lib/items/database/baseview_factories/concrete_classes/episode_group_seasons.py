from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.episode_groups import EpisodeGroupSeasons
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.episode_groups import EpisodeGroupsList


class EpisodeGroupSeasonsList(EpisodeGroupsList):
    table = 'episode_group_seasons'
    parent_mediatype = 'episode_group'
    cached_data_conditions = 'group_id=? AND tvshow_id=? ORDER BY ordering'

    @cached_property
    def parent_precache_tvshow(self):
        return self.get_parent_data('tvshow')

    @cached_property
    def parent_database(self):
        database_obj = BaseItemFactory(self.parent_mediatype, common_apis=self.common_apis)
        database_obj.tmdb_id = self.group_id
        database_obj.tvshow_tmdb_id = self.tmdb_id
        database_obj.cache = self.cache
        database_obj.connection = self.connection
        database_obj.cache_refresh = self.cache_refresh
        return database_obj

    @cached_property
    def parent_item_data(self):
        if not self.tmdb_id or not self.parent_precache_tvshow:
            return
        return self.parent_database.data

    @property
    def cached_data_keys(self):
        return (*super().cached_data_keys, *EpisodeGroupSeasons.get_count_keys())

    @property
    def cached_data_values(self):
        return (self.group_id, self.item_id)


class Tvshow(EpisodeGroupSeasonsList):
    pass
