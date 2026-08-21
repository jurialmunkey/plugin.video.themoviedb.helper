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
    data_key = None  # Returned as list at base level


class SyncWatched(MDbListDataTypeEpisodesNotShows):
    keys = ('plays', 'last_watched_at', 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at', )
    last_activities_key = 'watched_at'
    method = 'sync/watched'

    @property
    def sync_kwgs(self):
        sync_kwgs = {'mediatype': self.item_type}
        return sync_kwgs


class SyncNextEpisodes(MDbListDataType):  # TODO: Check if should be basic datatype not episodes
    keys = ('next_episode_id', 'next_episode_aired_at', 'last_watched_at', )
    last_activities_key = 'watched_at'
    method = 'upnext'
    sync_kwgs = {}
    expiry_time = HALFDAY_EXPIRY
    data_key = 'items'  # Uses old style API with list in items key
