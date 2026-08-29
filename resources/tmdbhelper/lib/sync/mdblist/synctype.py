from tmdbhelper.lib.sync.mdblist.datatype import MDbListDataType, MDbListDataTypeEpisodesInShows, MDbListDataTypeEpisodesNotShows
from tmdbhelper.lib.addon.consts import HALFDAY_EXPIRY


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


class SyncNextEpisodes(MDbListDataType):  # TODO: Check if should be basic datatype not episodes
    keys = ('next_episode_id', 'next_episode_aired_at', 'last_watched_at', )
    last_activities_key = 'watched_at'
    method = 'upnext'
    sync_kwgs = {}
    expiry_time = HALFDAY_EXPIRY

    def get_data_list_by_type(self, data):
        try:
            return data['items']  # API list style
        except KeyError:
            pass


class SyncWatched(MDbListDataTypeEpisodesNotShows):
    keys = ('plays', 'last_watched_at', )  # 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at',
    last_activities_key = 'watched_at'
    method = 'sync/watched'
    aggregate_key = 'plays'  # TODO: Consider more efficient way of collecting play counts (currently disabled plays=all kwgs)

    def clear_columns(self, *args, **kwargs):
        if self.timestamp:  # Skip clearing columns if we just update
            return
        super().clear_columns(*args, **kwargs)

    @property
    def sync_kwgs(self):
        sync_kwgs = (
            ('mediatype', self.item_type),
            ('since', self.timestamp),  # TODO: DO THIS WITH JOURNAL INSTEAD AND REMOVE ITEMS too
        )
        return {k: v for k, v in sync_kwgs if v}
