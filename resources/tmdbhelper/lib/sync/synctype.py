from tmdbhelper.lib.addon.plugin import get_setting
import tmdbhelper.lib.sync.trakt.synctype as trakt_synctype
import tmdbhelper.lib.sync.mdblist.synctype as mdblist_synctype


SyncHiddenProgressWatched = trakt_synctype.SyncHiddenProgressWatched
SyncHiddenProgressCollected = trakt_synctype.SyncHiddenProgressCollected
SyncHiddenCalendar = trakt_synctype.SyncHiddenCalendar
SyncHiddenDropped = trakt_synctype.SyncHiddenDropped
SyncRatings = trakt_synctype.SyncRatings
SyncFavorites = trakt_synctype.SyncFavorites
SyncAllNextEpisodes = trakt_synctype.SyncAllNextEpisodes


def SyncWatchlistFactory():
    if get_setting('sync_source_watchlist', 'str') == 'MDbList':
        return mdblist_synctype.SyncWatchlist
    return trakt_synctype.SyncWatchlist


SyncWatchlist = SyncWatchlistFactory()


def SyncCollectionFactory():
    if get_setting('sync_source_collection', 'str') == 'MDbList':
        return mdblist_synctype.SyncCollection
    return trakt_synctype.SyncCollection


SyncCollection = SyncCollectionFactory()


def SyncPlaybackFactory():
    if get_setting('sync_source_playback', 'str') == 'MDbList':
        return mdblist_synctype.SyncPlayback
    return trakt_synctype.SyncPlayback


SyncPlayback = SyncPlaybackFactory()


def SyncNextEpisodesFactory():
    if get_setting('sync_source_upnext', 'str') == 'MDbList':
        return mdblist_synctype.SyncNextEpisodes
    return trakt_synctype.SyncNextEpisodes


SyncNextEpisodes = SyncNextEpisodesFactory()


def SyncWatchedFactory():
    if get_setting('sync_source_watched', 'str') == 'MDbList':
        return mdblist_synctype.SyncWatched
    return trakt_synctype.SyncWatched


SyncWatched = SyncWatchedFactory()
