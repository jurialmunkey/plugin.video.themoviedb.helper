from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.sync.lists_nextmovies import ListNextMoviesProperties
from tmdbhelper.lib.items.directories.sync.mapper_currentlywatchingmovies import FactoryCurrentlyWatchingMoviesItemMapper


class ListCurrentlyWatchingMoviesProperties(ListNextMoviesProperties):
    item_mapper_class = staticmethod(FactoryCurrentlyWatchingMoviesItemMapper)

    @cached_property
    def playback_items(self):
        return self.get_playback_items()

    def get_playback_items(self):
        getter = self.syncdata.get_all_playback_getter('movie')
        getter.additional_keys = ('playback_paused_at', )
        return sorted(
            (item for item in getter.items if 0 < item['playback_progress'] < 100),
            key=lambda item: item['playback_paused_at'] or '', reverse=True)

    def get_sync_data(self):
        if not self.provider_available:
            return []
        entries = {
            item['tmdb_id']: dict(item, last_activity_at=item['last_watched_at'])
            for item in super().get_sync_data()
        }
        for item in self.playback_items:
            entries.setdefault(item['tmdb_id'], dict(item, last_activity_at=item['playback_paused_at']))
        return sorted(entries.values(), key=lambda item: item['last_activity_at'] or '', reverse=True)
