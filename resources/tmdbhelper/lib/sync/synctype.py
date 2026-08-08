from tmdbhelper.lib.addon.plugin import get_setting
import tmdbhelper.lib.sync.trakt.synctype as trakt_synctype
import tmdbhelper.lib.sync.mdblist.synctype as mdblist_synctype


SyncHiddenProgressWatched = trakt_synctype.SyncHiddenProgressWatched
SyncHiddenProgressCollected = trakt_synctype.SyncHiddenProgressCollected
SyncHiddenCalendar = trakt_synctype.SyncHiddenCalendar
SyncHiddenDropped = trakt_synctype.SyncHiddenDropped
SyncWatched = trakt_synctype.SyncWatched
SyncPlayback = trakt_synctype.SyncPlayback
SyncRatings = trakt_synctype.SyncRatings
SyncFavorites = trakt_synctype.SyncFavorites
SyncAllNextEpisodes = trakt_synctype.SyncAllNextEpisodes
SyncNextEpisodesMetaItem = trakt_synctype.SyncNextEpisodesMetaItem
SyncNextEpisodesMeta = trakt_synctype.SyncNextEpisodesMeta
SyncNextEpisodes = trakt_synctype.SyncNextEpisodes


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
