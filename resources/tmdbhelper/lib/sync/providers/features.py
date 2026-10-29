FEATURE_LABELS = {'watched': 32408, 'watchlist': 32193, 'collection': 32192,
                  'scrobbling': 32138, 'stats': 32598}

SYNC_FEATURES = {
    'SyncWatched': 'watched', 'SyncPlayback': 'watched',
    'SyncNextEpisodes': 'watched', 'SyncAllNextEpisodes': 'watched',
    'SyncAiredEpisodes': 'watched', 'SyncHiddenProgressWatched': 'watched',
    'SyncHiddenCalendar': 'watched', 'SyncHiddenDropped': 'watched',
    'SyncCollection': 'collection', 'SyncHiddenProgressCollected': 'collection',
    'SyncWatchlist': 'watchlist',
}

ACTION_FEATURES = {
    'watched': 'watched', 'unwatched': 'watched', 'progress': 'watched',
    'dropped': 'watched', 'watchlist': 'watchlist', 'collection': 'collection',
}

ITEM_ACTIONS = ('watched', 'unwatched', 'progress', 'dropped', 'watchlist', 'collection')

WATCHED_GETTERS = ('movies_to_watch', 'shows_to_watch', 'shows_in_progress')
