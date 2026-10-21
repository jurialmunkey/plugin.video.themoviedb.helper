from tmdbhelper.lib.addon.plugin import get_setting
import tmdbhelper.lib.sync.trakt.synctype as trakt_synctype
import tmdbhelper.lib.sync.mdblist.synctype as mdblist_synctype
import tmdbhelper.lib.sync.floppy.synctype as floppy_synctype


SYNC_SOURCE_MODULES = {
    'Trakt': trakt_synctype,
    'MDbList': mdblist_synctype,
    'Floppy': floppy_synctype,
}


def get_synctype(source, name):
    """ Get sync type class from the provider selected in setting sync_source_{source} (Trakt by default) """
    return getattr(SYNC_SOURCE_MODULES.get(get_setting(f'sync_source_{source}', 'str'), trakt_synctype), name)


def SyncHiddenProgressWatched():
    return get_synctype('watched', 'SyncHiddenProgressWatched')


def SyncHiddenProgressCollected():
    return get_synctype('collection', 'SyncHiddenProgressCollected')


def SyncHiddenCalendar():
    return get_synctype('watched', 'SyncHiddenCalendar')


def SyncHiddenDropped():
    return get_synctype('watched', 'SyncHiddenDropped')


def SyncRatings():
    return trakt_synctype.SyncRatings


def SyncFavorites():
    return trakt_synctype.SyncFavorites


def SyncAllNextEpisodes():
    return get_synctype('collection', 'SyncAllNextEpisodes')


def SyncWatchlist():
    return get_synctype('watchlist', 'SyncWatchlist')


def SyncCollection():
    return get_synctype('collection', 'SyncCollection')


def SyncPlayback():
    return get_synctype('watched', 'SyncPlayback')


def SyncNextEpisodes():
    return get_synctype('watched', 'SyncNextEpisodes')


def SyncWatched():
    return get_synctype('watched', 'SyncWatched')


def SyncAiredEpisodes():
    if get_setting('sync_source_watched', 'str') == 'MDbList':
        return SyncNextEpisodes()  # AIRED/WATCHED counts in next episodes for MDbList
    return SyncWatched()
