from tmdbhelper.lib.addon.consts import HALFDAY_EXPIRY
from tmdbhelper.lib.sync.datatype import timerlock
from tmdbhelper.lib.sync.trakt.datatype import TraktDataType, TraktDataTypeEpisodesInShows, TraktDataTypeShowsToEpisodes


class SyncHiddenProgressWatched(TraktDataType):
    keys = ('hidden_at', )
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_watched'
    key_prefix = 'progress_watched'

    @timerlock
    def sync_func(self):
        """ Get items that are hidden on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.__class__.__name__} get_response_sync users {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync(
                'users', self.method,
                type=f'{self.item_type}s'
            )


class SyncHiddenProgressCollected(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_collected'
    key_prefix = 'progress_collected'


class SyncHiddenCalendar(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/calendar'
    key_prefix = 'calendar'


class SyncHiddenDropped(SyncHiddenProgressWatched):
    last_activities_key = 'dropped_at'
    method = 'hidden/dropped'
    key_prefix = 'dropped'


class SyncWatched(TraktDataTypeEpisodesInShows):
    keys = ('plays', 'last_watched_at', 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at', )
    last_activities_key = 'watched_at'
    sync_kwgs = {'extended': 'full,progress'}
    method = 'watched'


class SyncPlayback(TraktDataTypeShowsToEpisodes):
    keys = ('progress', 'paused_at', 'id', )
    last_activities_key = 'paused_at'
    sync_kwgs = {'extended': 'full'}
    method = 'playback'
    key_prefix = 'playback'


class SyncRatings(TraktDataType):
    keys = ('rating', 'rated_at', )
    last_activities_key = 'rated_at'
    method = 'ratings'


class SyncFavorites(TraktDataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'favorited_at'
    sync_kwgs = {'extended': 'full'}
    method = 'favorites'
    key_prefix = 'favorites'


class SyncWatchlist(TraktDataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'watchlisted_at'
    sync_kwgs = {'extended': 'full'}
    method = 'watchlist'
    key_prefix = 'watchlist'


class SyncCollection(TraktDataTypeEpisodesInShows):
    keys = ('last_collected_at', 'last_updated_at', )
    last_activities_key = 'collected_at'
    method = 'collection'
    key_prefix = 'collection'


class SyncAllNextEpisodes(TraktDataTypeEpisodesInShows):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.sync.trakt.nextmeta import TraktSyncAllNextEpisodesMeta
        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return TraktSyncAllNextEpisodesMeta(self).items


class SyncNextEpisodes(SyncAllNextEpisodes):
    keys = ('next_episode_id', 'next_episode_aired_at')
    last_activities_key = 'watched_at'
    method = 'nextup'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.sync.trakt.nextmeta import TraktSyncNextEpisodesMeta
        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return TraktSyncNextEpisodesMeta(self).items
