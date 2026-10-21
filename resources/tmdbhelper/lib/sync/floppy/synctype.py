from tmdbhelper.lib.addon.consts import HALFDAY_EXPIRY
from tmdbhelper.lib.sync.datatype import timerlock
from tmdbhelper.lib.sync.floppy.datatype import (
    FloppyDataType,
    FloppyDataTypeEpisodesInShows,
    FloppyDataTypeShowsToEpisodes,
    FloppyDataTypeNull,
)
from tmdbhelper.lib.sync.floppy.dataconf import (
    FloppyWatchlist,
    FloppyDropped,
    FloppyNextEpisodes,
    FloppyWatchedMovies,
    FloppyWatchedShows,
    FloppyPlayback,
)


class SyncWatchedBase(FloppyDataTypeEpisodesInShows):
    keys = ('plays', 'last_watched_at', 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at', )
    last_activities_key = 'watched_at'
    method = 'watched'
    tracking_status_param = None  # Status filter applies to the default entry so filter each play client side


class SyncWatchedMovies(SyncWatchedBase):
    record_list_class = FloppyWatchedMovies


class SyncWatchedShows(SyncWatchedBase):

    def get_response_sync(self, *paths, **kwargs):
        show_entries = self.get_response_sync_entries(*paths, **kwargs)
        if show_entries is None:
            return
        episode_entries = self.get_response_sync_data('media', 'episode', **kwargs)
        if episode_entries is None:
            return
        return FloppyWatchedShows(show_entries, episode_entries).data


class SyncWatchedFactory(SyncWatchedBase):

    def __new__(cls, instance_syncdata, item_type):
        routes = {
            'movie': SyncWatchedMovies,
            'show': SyncWatchedShows,
            'season': SyncWatchedShows,
            'episode': SyncWatchedShows,
        }
        return routes[item_type](instance_syncdata, item_type)


SyncWatched = SyncWatchedFactory


class SyncPlayback(FloppyDataTypeShowsToEpisodes):
    keys = ('progress', 'paused_at', 'id', )
    last_activities_key = 'paused_at'
    method = 'playback'
    key_prefix = 'playback'
    record_list_class = FloppyPlayback

    @property
    def sync_args(self):
        return (('playback', 'progress', ), )

    @property
    def sync_kwgs(self):
        return {'media_type': self.item_type, 'completed': 'false'}


class SyncWatchlist(FloppyDataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'watchlisted_at'
    method = 'watchlist'
    key_prefix = 'watchlist'
    record_list_class = FloppyWatchlist


class SyncCollection(FloppyDataTypeNull):
    last_activities_key = 'collected_at'
    method = 'collection'
    key_prefix = 'collection'


class SyncNextEpisodes(FloppyDataTypeEpisodesInShows):
    keys = ('next_episode_id', 'next_episode_aired_at', )
    last_activities_key = 'watched_at'
    method = 'nextup'
    expiry_time = HALFDAY_EXPIRY
    record_list_class = FloppyNextEpisodes


class SyncAllNextEpisodes(FloppyDataTypeEpisodesInShows):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes from watched Floppy episodes """
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.sync.floppy.nextmeta import FloppySyncAllNextEpisodesMeta
        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return FloppySyncAllNextEpisodesMeta(self).items


class SyncHiddenProgressWatched(FloppyDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_watched'
    key_prefix = 'progress_watched'


class SyncHiddenProgressCollected(FloppyDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_collected'
    key_prefix = 'progress_collected'


class SyncHiddenCalendar(FloppyDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/calendar'
    key_prefix = 'calendar'


class SyncHiddenDropped(FloppyDataType):
    keys = ('hidden_at', )
    last_activities_key = 'dropped_at'
    method = 'dropped'
    key_prefix = 'dropped'
    record_list_class = FloppyDropped
