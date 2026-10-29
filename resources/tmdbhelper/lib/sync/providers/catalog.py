PROVIDERS = {
    'script.module.tmdbhelper.sync.trakt': {
        'provider_id': 'trakt',
        'display_name': 'Trakt',
        'capabilities': ('watched', 'watchlist', 'collection', 'scrobbling', 'lists', 'ratings', 'monitor_lists', 'imdb_top250', 'stats'),
    },
    'script.module.tmdbhelper.sync.mdblist': {
        'provider_id': 'mdblist',
        'display_name': 'MDbList',
        'capabilities': ('watched', 'watchlist', 'collection', 'scrobbling', 'lists', 'ratings', 'monitor_lists', 'service_actions'),
    },
    'script.module.tmdbhelper.sync.kodi': {
        'provider_id': 'kodi',
        'display_name': 'Kodi',
        'capabilities': ('watched', 'collection', 'scrobbling'),
    },
}
