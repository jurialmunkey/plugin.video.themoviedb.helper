from tmdbhelper.lib.sync.mdblist.datatype import MDbListDataType, MDbListDataTypeEpisodesInShows, MDbListDataTypeEpisodesToShows, MDbListDataTypeNull
from tmdbhelper.lib.sync.mdblist.dataconf import configure_episode_list
from tmdbhelper.lib.addon.consts import HALFDAY_EXPIRY
from tmdbhelper.lib.sync.datatype import timerlock


class SyncWatchlist(MDbListDataType):
    keys = ('rank', 'listed_at', 'notes', )  # TODO: FIXME notes and rank?
    last_activities_key = 'watchlisted_at'
    method = 'watchlist/items'
    key_prefix = 'watchlist'

    @property
    def sync_kwgs(self):
        sync_kwgs = {'mediatype': self.item_type}
        return sync_kwgs


class SyncCollection(MDbListDataType):
    keys = ('last_collected_at', 'last_updated_at', )
    last_activities_key = 'collected_at'
    method = 'sync/collection'
    key_prefix = 'collection'

    @property
    def sync_kwgs(self):
        sync_kwgs = {'mediatype': self.item_type}
        return sync_kwgs


class SyncPlayback(MDbListDataTypeEpisodesInShows):
    keys = ('progress', 'paused_at', 'id', )
    last_activities_key = 'paused_at'
    sync_kwgs = {}
    method = 'sync/playback'
    key_prefix = 'playback'

    def get_data_list_by_type(self, data):
        return data  # Data comes as a list already


class SyncNextEpisodes(MDbListDataType):
    keys = ('next_episode_id', 'next_episode_aired_at', 'last_watched_at', 'aired_episodes', 'watched_episodes', )  # AIRED AND WATCHED DATA IN THIS ENDPOINT FOR MDBLIST
    last_activities_key = 'watched_at'
    method = 'upnext'
    sync_kwgs = {}
    expiry_time = HALFDAY_EXPIRY

    def get_data_list_by_type(self, data):
        try:
            return data['items']  # API list style
        except KeyError:
            pass


class SyncWatched(MDbListDataTypeEpisodesToShows):
    keys = ('plays', 'last_watched_at', )  # 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at',
    last_activities_key = 'watched_at'
    method = 'sync/watched'

    def get_data_list_by_type(self, data):
        try:
            return data[f'{self.sync_kwgs_mediatype}s']
        except KeyError:
            return

    def get_response_sync(self, *args, **kwargs):
        data = super().get_response_sync(*args, **kwargs)
        return configure_episode_list(data) if data and self.sync_kwgs_mediatype == 'episode' else data

    def clear_columns(self, *args, **kwargs):
        if self.timestamp:  # Skip clearing columns if we just update
            return
        super().clear_columns(*args, **kwargs)

    @property
    def sync_kwgs_mediatype(self):
        if self.item_type in ('show', 'season', 'episode'):
            return 'episode'
        return self.item_type

    @property
    def sync_kwgs(self):
        sync_kwgs = (
            ('mediatype', self.sync_kwgs_mediatype),
            ('since', self.timestamp),  # TODO: DO THIS WITH JOURNAL INSTEAD AND REMOVE ITEMS too
        )
        return {k: v for k, v in sync_kwgs if v}


class SyncAllNextEpisodes(MDbListDataTypeEpisodesInShows):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'
    expiry_time = HALFDAY_EXPIRY
    sync_kwgs = {}

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.sync.mdblist.nextmeta import MDbListSyncAllNextEpisodesMeta
        with TimerFunc(
            f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}',
            inline=True,
            log_threshold=0.001
        ):
            return MDbListSyncAllNextEpisodesMeta(self).items


class SyncHiddenProgressWatched(MDbListDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_watched'
    key_prefix = 'progress_watched'


class SyncHiddenProgressCollected(MDbListDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_collected'
    key_prefix = 'progress_collected'


class SyncHiddenCalendar(MDbListDataTypeNull):
    last_activities_key = 'hidden_at'
    method = 'hidden/calendar'
    key_prefix = 'calendar'
