from tmdbhelper.lib.addon.plugin import get_setting
import tmdbhelper.lib.sync.trakt.synctype as trakt_synctype
import tmdbhelper.lib.sync.mdblist.synctype as mdblist_synctype

SYNC_SOURCE_WATCHLIST = get_setting('sync_source_watchlist', 'str')

SyncHiddenProgressWatched = trakt_synctype.SyncHiddenProgressWatched
SyncHiddenProgressCollected = trakt_synctype.SyncHiddenProgressCollected
SyncHiddenCalendar = trakt_synctype.SyncHiddenCalendar
SyncHiddenDropped = trakt_synctype.SyncHiddenDropped
SyncWatched = trakt_synctype.SyncWatched
SyncPlayback = trakt_synctype.SyncPlayback
SyncRatings = trakt_synctype.SyncRatings
SyncFavorites = trakt_synctype.SyncFavorites
SyncCollection = trakt_synctype.SyncCollection
SyncAllNextEpisodes = trakt_synctype.SyncAllNextEpisodes
SyncNextEpisodesMetaItem = trakt_synctype.SyncNextEpisodesMetaItem
SyncNextEpisodesMeta = trakt_synctype.SyncNextEpisodesMeta
SyncNextEpisodes = trakt_synctype.SyncNextEpisodes


if SYNC_SOURCE_WATCHLIST == 'MDbList':
    SyncWatchlist = mdblist_synctype.SyncWatchlist
else:
    SyncWatchlist = trakt_synctype.SyncWatchlist
