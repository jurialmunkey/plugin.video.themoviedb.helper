from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.items.directories.lists_default import ListProperties, ListDefault
from tmdbhelper.lib.items.directories.tmdb.mapper_episode_groups import (
    EpisodeGroupItemMapper, EpisodeGroupSeasonItemMapper, EpisodeGroupEpisodeItemMapper,
)


class ListEpisodeGroupsProperties(ListProperties):

    item_mapper_class = EpisodeGroupItemMapper
    database_view_route = 'episode_groups'
    group_id = None
    season_group_id = None

    @cached_property
    def database_view(self):
        return BaseViewFactory(
            self.database_view_route, 'tv', self.tmdb_id,
            group_id=self.group_id, season_group_id=self.season_group_id)

    @cached_property
    def episode_groups(self):
        return self.database_view.data or []

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    @cached_property
    def items(self):
        return [
            self.get_mapped_item({'tmdb_id': self.tmdb_id, 'group': group})
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
        return list_properties

    def get_items(self, tmdb_id, group_id=None, season_group_id=None, **kwargs):
        self.list_properties.tmdb_type = 'tv'
        self.list_properties.tmdb_id = tmdb_id
        self.list_properties.group_id = group_id
        self.list_properties.season_group_id = season_group_id
        return self.get_items_finalised()


class ListEpisodeGroupSeasonsProperties(ListEpisodeGroupsProperties):

    item_mapper_class = EpisodeGroupSeasonItemMapper
    database_view_route = 'episode_group_seasons'

    @cached_property
    def plugin_category(self):
        return (self.database_view.parent_item_data or {}).get('infolabels', {}).get('title') or self.localized


class ListEpisodeGroupEpisodesProperties(ListEpisodeGroupSeasonsProperties):

    item_mapper_class = EpisodeGroupEpisodeItemMapper
    database_view_route = 'episode_group_season_episodes'
    container_content = 'episodes'


class ListEpisodeGroupSeasons(ListEpisodeGroups):
    list_properties_class = ListEpisodeGroupSeasonsProperties


class ListEpisodeGroupEpisodes(ListEpisodeGroups):
    list_properties_class = ListEpisodeGroupEpisodesProperties

    @cached_property
    def sort_methods(self):
        from xbmcplugin import SORT_METHOD_UNSORTED
        return [
            {'sortMethod': SORT_METHOD_UNSORTED, 'labelMask': '[%P. ]%T', 'label2Mask': '%D'},
        ]
