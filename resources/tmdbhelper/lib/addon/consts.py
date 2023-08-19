CACHE_SHORT, CACHE_MEDIUM, CACHE_LONG, CACHE_EXTENDED = 1, 7, 14, 90
ITER_PROPS_MAX = 10

TVDB_DISCLAIMER = 'Information provided by TheTVDB.com. Please consider supporting them. https://thetvdb.com/subscribe'

NODE_BASEDIR = 'special://profile/addon_data/plugin.video.themoviedb.helper/nodes/'

ACCEPTED_MEDIATYPES = [
    'video', 'movie', 'tvshow', 'season', 'episode', 'musicvideo', 'music', 'song', 'album', 'artist', 'set']

LANGUAGES = [
    'ar-AE', 'ar-SA', 'be-BY', 'bg-BG', 'bn-BD', 'ca-ES', 'ch-GU', 'cs-CZ', 'da-DK', 'de-AT', 'de-CH',
    'de-DE', 'el-GR', 'en-AU', 'en-CA', 'en-GB', 'en-IE', 'en-NZ', 'en-US', 'eo-EO', 'es-ES', 'es-MX',
    'et-EE', 'eu-ES', 'fa-IR', 'fi-FI', 'fr-CA', 'fr-FR', 'gl-ES', 'he-IL', 'hi-IN', 'hu-HU', 'id-ID',
    'it-IT', 'ja-JP', 'ka-GE', 'kk-KZ', 'kn-IN', 'ko-KR', 'lt-LT', 'lv-LV', 'ml-IN', 'ms-MY', 'ms-SG',
    'nb-NO', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'si-LK', 'sk-SK', 'sl-SI',
    'sr-RS', 'sv-SE', 'ta-IN', 'te-IN', 'th-TH', 'tl-PH', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-HK',
    'zh-TW', 'zu-ZA']

TMDB_PARAMS_SEASONS = {
    'info': 'details',
    'tmdb_type': 'tv',
    'tmdb_id': '{tmdb_id}',
    'season': '{season_number}'}

TMDB_PARAMS_EPISODES = {
    'info': 'details',
    'tmdb_type': 'tv',
    'tmdb_id': '{tmdb_id}',
    'season': '{season_number}',
    'episode': '{episode_number}'}

IMAGEPATH_ORIGINAL = 'https://image.tmdb.org/t/p/original'
IMAGEPATH_HIGH = 'https://image.tmdb.org/t/p/w1280'
IMAGEPATH_LOW = 'https://image.tmdb.org/t/p/w780'
IMAGEPATH_POSTER = 'https://image.tmdb.org/t/p/w500'
IMAGEPATH_SMALLPOSTER = 'https://image.tmdb.org/t/p/w342'
IMAGEPATH_SMALLLOGO = 'https://image.tmdb.org/t/p/w300'
IMAGEPATH_NEGATE = 'https://image.tmdb.org/t/p/h100_filter(negate,000,666)'
IMAGEPATH_ALL = [IMAGEPATH_ORIGINAL, IMAGEPATH_HIGH, IMAGEPATH_LOW, IMAGEPATH_POSTER, IMAGEPATH_SMALLPOSTER, IMAGEPATH_SMALLLOGO]
IMAGEPATH_QUALITY_POSTER = [IMAGEPATH_POSTER, IMAGEPATH_POSTER, IMAGEPATH_POSTER, IMAGEPATH_SMALLPOSTER]
IMAGEPATH_QUALITY_FANART = [IMAGEPATH_ORIGINAL, IMAGEPATH_HIGH, IMAGEPATH_HIGH, IMAGEPATH_LOW]
IMAGEPATH_QUALITY_THUMBS = [IMAGEPATH_ORIGINAL, IMAGEPATH_HIGH, IMAGEPATH_HIGH, IMAGEPATH_LOW]
IMAGEPATH_QUALITY_CLOGOS = [IMAGEPATH_ORIGINAL, IMAGEPATH_POSTER, IMAGEPATH_POSTER, IMAGEPATH_SMALLLOGO]
ARTWORK_BLACKLIST = [
    [],
    ['poster', 'season.poster', 'tvshow.poster'],
    ['fanart', 'season.fanart', 'tvshow.fanart', 'poster', 'season.poster', 'tvshow.poster'],
    ['fanart', 'season.fanart', 'tvshow.fanart', 'poster', 'season.poster', 'tvshow.poster']]

PLAYERS_URLENCODE = [
    'name', 'showname', 'clearname', 'tvshowtitle', 'title', 'thumbnail', 'poster', 'fanart',
    'originaltitle', 'plot', 'cast', 'actors']

PLAYERS_BASEDIR_USER = 'special://profile/addon_data/plugin.video.themoviedb.helper/players/'
PLAYERS_BASEDIR_SAVE = 'special://profile/addon_data/plugin.video.themoviedb.helper/reconfigured_players/'
PLAYERS_BASEDIR_BUNDLED = 'special://home/addons/plugin.video.themoviedb.helper/resources/players/'
PLAYERS_BASEDIR_TEMPLATES = 'special://home/addons/plugin.video.themoviedb.helper/resources/templates/'
PLAYERS_PRIORITY = 1000
PLAYERS_REQUIRED_IDS = ['{imdb}', '{tvdb}', '{trakt}', '{slug}', '{eptvdb}' '{epimdb}', '{eptrakt}', '{epslug}', '{epid}']
PLAYERS_CHOSEN_DEFAULTS_FILENAME = 'player_defaults'

NO_LABEL_FORMATTING = ['details', 'upcoming', 'trakt_calendar', 'trakt_myairing', 'trakt_anticipated', 'library_nextaired', 'library_airingnext', 'trakt_airingnext', 'videos', 'trakt_watchlist_anticipated']

PARAM_WIDGETS_RELOAD = 'reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]'
PARAM_WIDGETS_RELOAD_FORCED = 'reload=$INFO[System.Time(hh:mm:ss)]'

UPNEXT_EPISODE_ART = {
    'thumb': lambda li: li.art.get('thumb') or '',
    'tvshow.clearart': lambda li: li.art.get('tvshow.clearart') or '',
    'tvshow.clearlogo': lambda li: li.art.get('tvshow.clearlogo') or '',
    'tvshow.fanart': lambda li: li.art.get('tvshow.fanart') or '',
    'tvshow.landscape': lambda li: li.art.get('tvshow.landscape') or '',
    'tvshow.poster': lambda li: li.art.get('tvshow.poster') or '',
}

UPNEXT_EPISODE = {
    'episodeid': lambda li: li.unique_ids.get('tmdb') or '',
    'tvshowid': lambda li: li.unique_ids.get('tvshow.tmdb') or '',
    'title': lambda li: li.infolabels.get('title') or '',
    'art': lambda li: {k: v(li) for k, v in UPNEXT_EPISODE_ART.items()},
    'season': lambda li: li.infolabels.get('season') or 0,
    'episode': lambda li: li.infolabels.get('episode') or 0,
    'showtitle': lambda li: li.infolabels.get('tvshowtitle') or '',
    'plot': lambda li: li.infolabels.get('plot') or '',
    'playcount': lambda li: li.infolabels.get('playcount') or 0,
    'rating': lambda li: li.infolabels.get('rating') or 0,
    'firstaired': lambda li: li.infolabels.get('premiered') or '',
    'runtime': lambda li: li.infolabels.get('duration') or 0,
}

TMDB_ALL_ITEMS_LISTS = {
    'movie': {
        'type': 'movie',
        'sort': False,
        'limit': 20
    },
    'tv': {
        'type': 'tv_series',
        'sort': False,
        'limit': 20
    },
    'person': {
        'type': 'person',
        'sort': False,
        'limit': 20
    },
    'collection': {
        'type': 'collection',
        'sort': False,
        'limit': 20,
        'params': {
            'info': 'collection',
            'tmdb_id': '{tmdb_id}',
            'tmdb_type': 'collection',
            'plugin_category': '{label}'}
    },
    'network': {
        'type': 'tv_network',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'tv',
            'with_networks': '{tmdb_id}', 'with_id': 'True',
            'plugin_category': '{label}'}
    },
    'keyword': {
        'type': 'keyword',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'movie',
            'with_keywords': '{tmdb_id}', 'with_id': 'True',
            'plugin_category': '{label}'}
    },
    'studio': {
        'type': 'production_company',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'movie',
            'with_companies': '{tmdb_id}', 'with_id': 'True',
            'plugin_category': '{label}'}
    }
}

RANDOMISED_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.items.randomdir',
    'import_attr': 'ListRandom'}
RANDOMISED_LISTS = {
    'random_genres': {
        'params': {'info': 'genres'},
        'route': RANDOMISED_LISTS_ROUTE},
    'random_keyword': {
        'params': {'info': 'all_items', 'tmdb_type': 'keyword'},
        'route': RANDOMISED_LISTS_ROUTE},
    'random_trendinglists': {
        'params': {'info': 'trakt_trendinglists'},
        'route': RANDOMISED_LISTS_ROUTE},
    'random_popularlists': {
        'params': {'info': 'trakt_popularlists'},
        'route': RANDOMISED_LISTS_ROUTE},
    'random_likedlists': {
        'params': {'info': 'trakt_likedlists'},
        'route': RANDOMISED_LISTS_ROUTE},
    'random_mylists': {
        'params': {'info': 'trakt_mylists'},
        'route': RANDOMISED_LISTS_ROUTE}}

RANDOMISED_TRAKT_ROUTE = {
    'module_name': 'tmdbhelper.lib.items.randomdir',
    'import_attr': 'ListTraktRandom'}
RANDOMISED_TRAKT = {
    'random_trending': {
        'info': 'trakt_trending',
        'route': RANDOMISED_TRAKT_ROUTE},
    'random_popular': {
        'info': 'trakt_popular',
        'route': RANDOMISED_TRAKT_ROUTE},
    'random_mostplayed': {
        'info': 'trakt_mostplayed',
        'route': RANDOMISED_TRAKT_ROUTE},
    'random_mostviewers': {
        'info': 'trakt_mostviewers',
        'route': RANDOMISED_TRAKT_ROUTE},
    'random_anticipated': {
        'info': 'trakt_anticipated',
        'route': RANDOMISED_TRAKT_ROUTE}}

TMDB_SORT_TYPES = {'int': int, 'float': float, 'str': str}
TMDB_STACKED_CREDITS_PROPERTIES = [
    ('infoproperties', 'job'),
    ('infoproperties', 'character'),
    ('infoproperties', 'role')]
TMDB_COMBO_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.tmdb.lists',
    'import_attr': 'ListCombo'}
TMDB_BASIC_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.tmdb.lists',
    'import_attr': 'ListBasic'}
TMDB_BASIC_LISTS = {
    'popular': {
        'path': '{tmdb_type}/popular',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32175
    },
    'top_rated': {
        'path': '{tmdb_type}/top_rated',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32176
    },
    'upcoming': {
        'path': '{tmdb_type}/upcoming',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32177
    },
    'trending_day': {
        'path': 'trending/{tmdb_type}/day',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32178
    },
    'trending_week': {
        'path': 'trending/{tmdb_type}/week',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32179
    },
    'now_playing': {
        'path': '{tmdb_type}/now_playing',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32180
    },
    'airing_today': {
        'path': '{tmdb_type}/airing_today',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32181
    },
    'on_the_air': {
        'path': '{tmdb_type}/on_the_air',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32182
    },
    'recommendations': {
        'path': '{tmdb_type}/{tmdb_id}/recommendations',
        'key': 'results',
        'dbid_sorting': True,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'similar': {
        'path': '{tmdb_type}/{tmdb_id}/similar',
        'key': 'results',
        'dbid_sorting': True,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'stars_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'cast',
        'tmdb_type': 'movie',
        'sort_key': 'popularity',
        'sort_type': 'float',
        'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
        'dbid_sorting': True,
        'limit': 20,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'stars_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'cast',
        'sort_key': 'popularity',
        'sort_type': 'float',
        'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
        'dbid_sorting': True,
        'tmdb_type': 'tv',
        'limit': 20,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'stars_in_both': {
        'info_path_models': [
            {
                'path': 'person/{tmdb_id}/movie_credits',
                'tmdb_type': 'movie',
                'key': 'cast',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
            {
                'path': 'person/{tmdb_id}/tv_credits',
                'tmdb_type': 'tv',
                'key': 'cast',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
        ],
        'sort_key': 'popularity',
        'sort_type': 'float',
        'tmdb_type': 'both',
        'dbid_sorting': True,
        'limit': 20,
        'route': TMDB_COMBO_LISTS_ROUTE
    },
    'crew_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'crew',
        'sort_key': 'popularity',
        'sort_type': 'float',
        'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
        'dbid_sorting': True,
        'tmdb_type': 'movie',
        'limit': 20,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'crew_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'crew',
        'sort_key': 'popularity',
        'sort_type': 'float',
        'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
        'dbid_sorting': True,
        'tmdb_type': 'tv',
        'limit': 20,
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'crew_in_both': {
        'info_path_models': [
            {
                'path': 'person/{tmdb_id}/movie_credits',
                'tmdb_type': 'movie',
                'key': 'crew',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
            {
                'path': 'person/{tmdb_id}/tv_credits',
                'tmdb_type': 'tv',
                'key': 'crew',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
        ],
        'sort_key': 'popularity',
        'sort_type': 'float',
        'tmdb_type': 'both',
        'dbid_sorting': True,
        'limit': 20,
        'route': TMDB_COMBO_LISTS_ROUTE
    },
    'credits_in_both': {
        'info_path_models': [
            {
                'path': 'person/{tmdb_id}/movie_credits',
                'tmdb_type': 'movie',
                'key': 'cast',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
            {
                'path': 'person/{tmdb_id}/tv_credits',
                'tmdb_type': 'tv',
                'key': 'cast',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
            {
                'path': 'person/{tmdb_id}/movie_credits',
                'tmdb_type': 'movie',
                'key': 'crew',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
            {
                'path': 'person/{tmdb_id}/tv_credits',
                'tmdb_type': 'tv',
                'key': 'crew',
                'sort_key': 'popularity',
                'sort_type': 'float',
                'stacked': TMDB_STACKED_CREDITS_PROPERTIES,
                'limit': 20,
            },
        ],
        'sort_key': 'popularity',
        'sort_type': 'float',
        'tmdb_type': 'both',
        'dbid_sorting': True,
        'limit': 20,
        'route': TMDB_COMBO_LISTS_ROUTE
    },
    'images': {
        'path': 'person/{tmdb_id}/images',
        'key': 'profiles',
        'tmdb_type': 'image',
        'imagepath_quality': 'ARTWORK_QUALITY_POSTER',
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'posters': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'posters',
        'tmdb_type': 'image',
        'imagepath_quality': 'ARTWORK_QUALITY_POSTER',
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'fanart': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'backdrops',
        'tmdb_type': 'image',
        'imagepath_quality': 'ARTWORK_QUALITY_FANART',
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'episode_thumbs': {
        'path': 'tv/{tmdb_id}/season/{season}/episode/{episode}/images',
        'key': 'stills',
        'tmdb_type': 'image',
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'reviews': {
        'path': '{tmdb_type}/{tmdb_id}/reviews',
        'key': 'results',
        'tmdb_type': 'review',
        'params': {
            'info': 'reviews',
            'tmdb_type': '{tmdb_type}',
            'tmdb_id': '{tmdb_id}'
        },
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'revenue_movies': {
        'path': 'discover/{tmdb_type}?sort_by=revenue.desc',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32184
    },
    'most_voted': {
        'path': 'discover/{tmdb_type}?sort_by=vote_count.desc',
        'key': 'results',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32185
    },
    'collection': {
        'path': 'collection/{tmdb_id}',
        'key': 'parts',
        'tmdb_type': 'movie',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32192
    },
    'movie_keywords': {
        'path': 'movie/{tmdb_id}/keywords',
        'key': 'keywords',
        'tmdb_type': 'keyword',
        'tmdb_cache_only': True,
        'params': {
            'info': 'discover',
            'tmdb_type': 'movie',
            'with_keywords': '{tmdb_id}',
            'with_id': 'True'
        },
        'route': TMDB_BASIC_LISTS_ROUTE
    },
    'genres': {
        'path': 'genre/{tmdb_type}/list',
        'key': 'genres',
        'tmdb_type': 'genre',
        'tmdb_cache_only': True,
        'params': {
            'info': 'discover',
            'tmdb_type': '{base_tmdb_type}',
            'with_genres': '{tmdb_id}',
            'with_id': 'True'
        },
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{plural}',
    },
    'watch_providers': {
        'path': 'watch/providers/{tmdb_type}?watch_region={iso_country}',
        'key': 'results',
        'tmdb_type': 'provider',
        'tmdb_cache_only': True,
        'params': {
            'info': 'discover',
            'tmdb_type': '{base_tmdb_type}',
            'with_watch_providers': '{provider_id}',
            'watch_region': '{iso_country}',
            'with_id': 'True'
        },
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{plural}',
    },
    'tmdb_list': {
        'path': 'list/{list_id}',
        'key': 'items',
        'route': TMDB_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 535
    }
}


TRAKT_BASIC_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.trakt.lists',
    'import_attr': 'ListBasic'}
TRAKT_BASIC_LISTS = {
    'trakt_trending': {
        'path': '{trakt_type}s/trending',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32204
    },
    'trakt_popular': {
        'path': '{trakt_type}s/popular',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32175
    },
    'trakt_mostplayed': {
        'path': '{trakt_type}s/played/weekly',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32205
    },
    'trakt_mostviewers': {
        'path': '{trakt_type}s/watched/weekly',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32414
    },
    'trakt_anticipated': {
        'path': '{trakt_type}s/anticipated',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32206
    },
    'trakt_boxoffice': {
        'path': '{trakt_type}s/boxoffice',
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32207
    },
    'trakt_recommendations': {
        'path': 'recommendations/{trakt_type}s?ignore_collected=true',
        'authorize': True,
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32198
    },
    'trakt_myairing': {
        'path': 'calendars/my/{trakt_type}s',
        'authorize': True,
        'stacked': True,
        'route': TRAKT_BASIC_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32405
    }
}


TRAKT_SYNC_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.trakt.lists',
    'import_attr': 'ListSync'}
TRAKT_SYNC_LISTS = {
    'trakt_collection': {
        'sync_type': 'collection',
        'sort_by': 'title',
        'sort_how': 'asc',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32192
    },
    'trakt_watchlist': {
        'sync_type': 'watchlist',
        'use_show_activity': True,
        'sort_by': 'unsorted',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32193
    },
    'trakt_watchlist_released': {
        'sync_type': 'watchlist',
        'use_show_activity': True,
        'sort_by': 'released',
        'sort_how': 'desc',
        'extended': 'full',
        'filters': {
            'filter_key': 'premiered',
            'filter_value': {
                'module': 'tmdbhelper.lib.addon.tmdate',
                'method': 'get_todays_date',
                'kwargs': {}},
            'filter_operator': 'lt',
            'exclude_key': 'premiered',
            'exclude_value': 'is_empty'},
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32456
    },
    'trakt_watchlist_anticipated': {
        'sync_type': 'watchlist',
        'use_show_activity': True,
        'sort_by': 'released',
        'sort_how': 'asc',
        'extended': 'full',
        'filters': {
            'exclude_key': 'premiered',
            'exclude_value': {
                'module': 'tmdbhelper.lib.addon.tmdate',
                'method': 'get_todays_date',
                'kwargs': {}},
            'exclude_operator': 'lt'},
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 32457
    },
    'trakt_history': {
        'sync_type': 'watched',
        'sort_by': 'watched',
        'sort_how': 'desc',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32194
    },
    'trakt_mostwatched': {
        'sync_type': 'watched',
        'sort_by': 'plays',
        'sort_how': 'desc',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32195
    },
    'trakt_inprogress': {
        'sync_type': 'playback',
        'sort_by': 'paused',
        'sort_how': 'desc',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{localized} {plural}',
        'localized': 32196
    },
    'trakt_favorites': {
        'sync_type': 'favorites',
        'sort_by': 'unsorted',
        'route': TRAKT_SYNC_LISTS_ROUTE,
        'plugin_category': '{plural} {localized}',
        'localized': 1036
    }
}


TRAKT_LIST_OF_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.trakt.lists',
    'import_attr': 'ListLists'}
TRAKT_LIST_OF_LISTS = {
    'trakt_inlists': {
        'path': '{trakt_type}s/{trakt_id}/lists/personal/popular',
        'route': TRAKT_LIST_OF_LISTS_ROUTE,
        'get_trakt_id': True,
        'plugin_category': '{localized}',
        'localized': 32232},
    'trakt_trendinglists': {
        'path': 'lists/trending',
        'route': TRAKT_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32208},
    'trakt_popularlists': {
        'path': 'lists/popular',
        'route': TRAKT_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32209},
    'trakt_likedlists': {
        'path': 'users/likes/lists',
        'authorize': True,
        'route': TRAKT_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32210},
    'trakt_mylists': {
        'path': 'users/me/lists',
        'authorize': True,
        'route': TRAKT_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32211}
}


MDBLIST_LIST_OF_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.api.mdblist.lists',
    'import_attr': 'ListLists'}
MDBLIST_LIST_OF_LISTS = {
    'mdblist_toplists': {
        'path': 'lists/top',
        'route': MDBLIST_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32421},
    'mdblist_yourlists': {
        'path': 'lists/user',
        'route': MDBLIST_LIST_OF_LISTS_ROUTE,
        'plugin_category': '{localized}',
        'localized': 32211},
}


ROUTE_NOID = {
    'dir_search': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.search',
        'import_attr': 'ListSearchDir'}},
    'dir_multisearch': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.search',
        'import_attr': 'ListMultiSearchDir'}},
    'search': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.search',
        'import_attr': 'ListSearch'}},
    'dir_discover': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.discover',
        'import_attr': 'ListDiscoverDir'}},
    'discover': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.discover',
        'import_attr': 'ListDiscover'}},
    'user_discover': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.discover',
        'import_attr': 'ListUserDiscover'}},
    'trakt_towatch': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListToWatch'}},
    'trakt_becauseyouwatched': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListBecauseYouWatched'}},
    'trakt_becausemostwatched': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListBecauseYouWatched'}},
    'trakt_calendar': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListCalendar'}},
    'library_nextaired': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListLibraryCalendar'}},
    'library_airingnext': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists_airingnext',
        'import_attr': 'ListLibraryAiringNext'}},
    'trakt_airingnext': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists_airingnext',
        'import_attr': 'ListTraktAiringNext'}},
    'trakt_inprogress': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListInProgress'}},
    'trakt_ondeck': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListOnDeck'}},
    'trakt_nextepisodes': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListNextEpisodes'}},
    'trakt_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListCustom'}},
    'trakt_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListCustomSearch'}},
    'trakt_sortby': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListSortBy'}},
    'trakt_comments': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListComments'}},
    'mdblist_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.api.mdblist.lists',
        'import_attr': 'ListCustom'}},
    'mdblist_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.api.mdblist.lists',
        'import_attr': 'ListCustomSearch'}},
    'all_items': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListAll'}},
    'dir_tvdb_awards': {'route': {
        'module_name': 'tmdbhelper.lib.api.tvdb.lists_awards',
        'import_attr': 'ListAwards'}},
    'dir_tvdb_award_categories': {'route': {
        'module_name': 'tmdbhelper.lib.api.tvdb.lists_awards',
        'import_attr': 'ListAwardCategories'}},
    'tvdb_award_category': {'route': {
        'module_name': 'tmdbhelper.lib.api.tvdb.lists_awards',
        'import_attr': 'ListAwardCategory'}},
    'dir_tvdb_genres': {'route': {
        'module_name': 'tmdbhelper.lib.api.tvdb.lists_genres',
        'import_attr': 'ListGenres'}},
    'tvdb_genre': {'route': {
        'module_name': 'tmdbhelper.lib.api.tvdb.lists_genres',
        'import_attr': 'ListGenre'}},
}


ROUTE_TMDBID = {
    'details': {'route': {
        'module_name': 'tmdbhelper.lib.items.basedir',
        'import_attr': 'ListDetails'}},
    'cast': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListCast'}},
    'crew': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListCrew'}},
    'videos': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListVideos'}},
    'seasons': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListSeasons'}},
    'flatseasons': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListFlatSeasons'}},
    'episodes': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListEpisodes'}},
    'episode_groups': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListEpisodeGroups'}},
    'episode_group_seasons': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListEpisodeGroupSeasons'}},
    'episode_group_episodes': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListEpisodeGroupEpisodes'}},
    'next_recommendation': {'route': {
        'module_name': 'tmdbhelper.lib.api.tmdb.lists',
        'import_attr': 'ListNextRecommendation'}},
    'trakt_upnext': {'route': {
        'module_name': 'tmdbhelper.lib.api.trakt.lists',
        'import_attr': 'ListUpNext'}},
}
