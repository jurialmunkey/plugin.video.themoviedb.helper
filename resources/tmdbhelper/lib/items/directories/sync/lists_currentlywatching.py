from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.sync.lists_standard import ListNextEpisodes, ListProviderSyncProperties
from tmdbhelper.lib.items.directories.sync.mapper_currentlywatching import CurrentlyWatchingItemMapper
from tmdbhelper.lib.sync.datasync import SyncDataFactory


class ListCurrentlyWatchingProperties(ListProviderSyncProperties):
    item_mapper_class = CurrentlyWatchingItemMapper

    @cached_property
    def syncdata(self):
        return SyncDataFactory()

    @cached_property
    def next_episode_items(self):
        return self.get_next_episode_items()

    def get_next_episode_items(self):
        getter = self.syncdata.get_all_unhidden_shows_nextepisode_getter()
        getter.additional_keys = ('last_watched_at', )
        return getter.items

    @cached_property
    def playback_items(self):
        return self.get_playback_items()

    def get_playback_items(self):
        getter = self.syncdata.get_currently_watching_playback_getter()
        return sorted(getter.items, key=lambda item: item['playback_paused_at'] or '', reverse=True)

    def get_sync_data(self):
        if not self.provider_available:
            return []
        entries = {
            item['tmdb_id']: dict(item, last_activity_at=item['last_watched_at'])
            for item in self.next_episode_items
        }
        for item in self.playback_items:
            entries.setdefault(item['tmdb_id'], dict(item, last_activity_at=item['playback_paused_at']))
        return sorted(entries.values(), key=lambda item: item['last_activity_at'] or '', reverse=True)

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if not self.response:
            return []
        return [self.get_mapped_item(item) for item in self.response.paginated_items.items]

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item


class ListCurrentlyWatching(ListNextEpisodes):
    list_properties_class = ListCurrentlyWatchingProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32600
        list_properties.sort_by = 'recentlywatched'
        return list_properties
