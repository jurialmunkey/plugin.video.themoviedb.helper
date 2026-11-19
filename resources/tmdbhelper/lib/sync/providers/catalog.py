PROVIDERS = {
    'script.module.tmdbhelper.sync.trakt': {
        'provider_id': 'trakt',
        'display_name': 'Trakt',
        'capabilities': (
            'watched',
            'watchlist',
            'collection',
            'scrobbling',
            'lists',
            'ratings',
            'monitor_lists',
            'imdb_top250',
            'list_actions',
        ),
    },
    'script.module.tmdbhelper.sync.mdblist': {
        'provider_id': 'mdblist',
        'display_name': 'MDbList',
        'capabilities': ('watched', 'watchlist', 'collection', 'scrobbling', 'lists', 'ratings', 'monitor_lists', 'service_actions'),
    },
    'script.module.tmdbhelper.sync.tvdb': {
        'provider_id': 'tvdb',
        'display_name': 'TVDb',
        'capabilities': ('lists',),
    },
    'script.module.tmdbhelper.sync.gemini': {
        'provider_id': 'gemini',
        'display_name': 'Gemini',
        'capabilities': ('lists',),
    },
    'script.module.tmdbhelper.sync.kodi': {
        'provider_id': 'kodi',
        'display_name': 'Kodi',
        'capabilities': ('watched', 'collection', 'scrobbling'),
    },
}
