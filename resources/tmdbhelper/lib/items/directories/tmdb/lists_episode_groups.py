from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.basemeta_factories.factory import BaseMetaFactory
from tmdbhelper.lib.items.directories.lists_default import ListProperties, ListDefault
from tmdbhelper.lib.items.directories.tmdb.mapper_episode_groups import EpisodeGroupItemMapper
from tmdbhelper.lib.items.listitem import ListItem


class ListEpisodeGroupsProperties(ListProperties):

    item_mapper_class = EpisodeGroupItemMapper

    @cached_property
    def tvshow_item(self):
        return self.lidc.get_item('tv', self.tmdb_id)

    @cached_property
    def episode_groups(self):
        if not self.tvshow_item:
            return []
        database_obj = BaseMetaFactory('episode_groups')
        database_obj.cache = self.lidc.cache
        database_obj.connection = self.lidc.connection
        database_obj.common_apis = self.lidc.common_apis
        database_obj.parent_id = f'tv.{self.tmdb_id}'
        return database_obj.cached_data or []

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    @cached_property
    def items(self):
        return [
            self.get_mapped_item({'tvshow_item': self.tvshow_item, 'group': group})
            for group in self.episode_groups
        ]


class ListEpisodeGroups(ListDefault):

    list_properties_class = ListEpisodeGroupsProperties
    is_detailed = True
    kodi_db = None

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32541
        list_properties.pagination = False
        list_properties.lidc = self.lidc
        return list_properties

    def get_items(self, tmdb_id, **kwargs):
        self.list_properties.tmdb_type = 'tv'
        self.list_properties.tmdb_id = tmdb_id
        return self.get_items_finalised()

    def build_detailed_items(self, items):
        # Full show details are already mapped; reloading them would replace group titles.
        return self.build_ratings_items([
            ListItem(parent_params=self.parent_params, **item) for item in items
        ])
