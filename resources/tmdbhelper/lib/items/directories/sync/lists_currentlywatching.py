from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.directories.sync.lists_standard import ListNextEpisodes, ListProviderSyncProperties
from tmdbhelper.lib.items.directories.sync.lists_currentlywatchingmovies import ListCurrentlyWatchingMoviesProperties
from tmdbhelper.lib.items.directories.sync.mapper_currentlywatching import CurrentlyWatchingItemMapper, FactoryCurrentlyWatchingItemMapper
from tmdbhelper.lib.sync.datasync import SyncDataFactory


class ListCurrentlyWatchingProperties(ListProviderSyncProperties):
    item_mapper_class = CurrentlyWatchingItemMapper

    @cached_property
    def plural(self):
        return self.get_plural()

    def get_plural(self):
        return convert_type(self.item_type, 'plural')

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
            ('episode', item['tmdb_id']): dict(item, item_type='episode', last_activity_at=item['last_watched_at'])
            for item in self.next_episode_items
        }
        for item in self.playback_items:
            entries.setdefault(
                ('episode', item['tmdb_id']),
                dict(item, item_type='episode', last_activity_at=item['playback_paused_at']))
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


class ListCurrentlyWatchingMixedProperties(ListCurrentlyWatchingProperties):
    item_mapper_class = staticmethod(FactoryCurrentlyWatchingItemMapper)

    @cached_property
    def movie_items(self):
        return self.get_movie_items()

    def get_movie_items(self):
        getter = self.syncdata.get_all_playback_getter('movie')
        getter.additional_keys = ('playback_paused_at', )
        return [
            dict(item, item_type='movie', last_activity_at=item['playback_paused_at'])
            for item in getter.items if 0 < item['playback_progress'] < 100
        ]

    def get_sync_data(self):
        if not self.provider_available:
            return []
        entries = {
            (item['item_type'], item['tmdb_id']): item
            for item in (*super().get_sync_data(), *self.movie_items)
        }
        return sorted(entries.values(), key=lambda item: item['last_activity_at'] or '', reverse=True)


class ListCurrentlyWatching(ListNextEpisodes):
    list_properties_class = ListCurrentlyWatchingProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32600
        list_properties.plugin_name = '{localized} {plural}'
        list_properties.sort_by = 'recentlywatched'
        return list_properties

    def get_items(self, tmdb_type, **kwargs):
        self.list_properties_class = {
            'movie': ListCurrentlyWatchingMoviesProperties,
            'both': ListCurrentlyWatchingMixedProperties,
        }.get(tmdb_type, ListCurrentlyWatchingProperties)
        item_type, container_content = {
            'movie': ('movie', 'movies'),
            'both': ('both', 'videos'),
        }.get(tmdb_type, ('episode', 'episodes'))
        self.list_properties.item_type = item_type
        self.list_properties.container_content = container_content
        return super().get_items(tmdb_type=tmdb_type, **kwargs)
