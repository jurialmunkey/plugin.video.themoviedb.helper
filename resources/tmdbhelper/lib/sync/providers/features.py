FEATURE_LABELS = {'watched': 32408, 'watchlist': 32193, 'collection': 32192,
                  'ratings': 563, 'favorites': 1036, 'scrobbling': 32138}

SYNC_FEATURES = {
    'SyncWatched': 'watched', 'SyncPlayback': 'watched',
    'SyncNextEpisodes': 'watched', 'SyncAllNextEpisodes': 'watched',
    'SyncAiredEpisodes': 'watched', 'SyncHiddenProgressWatched': 'watched',
    'SyncHiddenCalendar': 'watched', 'SyncHiddenDropped': 'watched',
    'SyncCollection': 'collection', 'SyncHiddenProgressCollected': 'collection',
    'SyncWatchlist': 'watchlist', 'SyncRatings': 'ratings', 'SyncFavorites': 'favorites',
}

ACTION_FEATURES = {
    'watched': 'watched', 'unwatched': 'watched', 'progress': 'watched',
    'dropped': 'watched', 'watchlist': 'watchlist', 'collection': 'collection',
    'favorites': 'favorites',
}

ITEM_ACTIONS = ('watched', 'unwatched', 'progress', 'dropped', 'watchlist', 'collection',
                'favorites')
