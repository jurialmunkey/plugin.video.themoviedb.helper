CACHE_SHORT, CACHE_MEDIUM, CACHE_LONG, CACHE_EXTENDED = 1, 7, 14, 90
ITER_PROPS_MAX = 10

DAY_IN_SECONDS = 86400
DEFAULT_EXPIRY = DAY_IN_SECONDS * 30
SHORTER_EXPIRY = DAY_IN_SECONDS * 7
TEMPDAY_EXPIRY = DAY_IN_SECONDS
HALFDAY_EXPIRY = DAY_IN_SECONDS * 0.5

DATALEVEL_OFF = 0
DATALEVEL_MIN = 1
DATALEVEL_MAX = 5

TVDB_DISCLAIMER = 'Information provided by TheTVDB.com. Please consider supporting them. https://thetvdb.com/subscribe'

NODE_BASEDIR = 'special://profile/addon_data/plugin.video.themoviedb.helper/nodes/'

LANGUAGES = (
    'ar-AE', 'ar-SA', 'be-BY', 'bg-BG', 'bn-BD', 'ca-ES', 'ch-GU', 'cs-CZ', 'da-DK', 'de-AT', 'de-CH',
    'de-DE', 'el-GR', 'en-AU', 'en-CA', 'en-GB', 'en-IE', 'en-NZ', 'en-US', 'eo-EO', 'es-ES', 'es-MX',
    'et-EE', 'eu-ES', 'fa-IR', 'fi-FI', 'fr-CA', 'fr-FR', 'gl-ES', 'he-IL', 'hi-IN', 'hu-HU', 'id-ID',
    'it-IT', 'ja-JP', 'ka-GE', 'kk-KZ', 'kn-IN', 'ko-KR', 'lt-LT', 'lv-LV', 'ml-IN', 'ms-MY', 'ms-SG',
    'nb-NO', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'si-LK', 'sk-SK', 'sl-SI',
    'sr-RS', 'sv-SE', 'ta-IN', 'te-IN', 'th-TH', 'tl-PH', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-HK',
    'zh-TW', 'zu-ZA')

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
IMAGEPATH_LARGEFANART = 'https://image.tmdb.org/t/p/w1280'
IAMGEPATH_SMALLFANART = 'https://image.tmdb.org/t/p/w780'
IMAGEPATH_LARGEPOSTER = 'https://image.tmdb.org/t/p/w780'
IMAGEPATH_BASICPOSTER = 'https://image.tmdb.org/t/p/w500'
IMAGEPATH_SMALLPOSTER = 'https://image.tmdb.org/t/p/w342'
IMAGEPATH_LARGELOGO = 'https://image.tmdb.org/t/p/w500'
IMAGEPATH_SMALLLOGO = 'https://image.tmdb.org/t/p/w300'
IMAGEPATH_NEGATE = 'https://image.tmdb.org/t/p/h100_filter(negate,000,666)'
IMAGEPATH_QUALITY_POSTER = (IMAGEPATH_LARGEPOSTER, IMAGEPATH_BASICPOSTER, IMAGEPATH_BASICPOSTER, IMAGEPATH_SMALLPOSTER, IMAGEPATH_ORIGINAL)
IMAGEPATH_QUALITY_FANART = (IMAGEPATH_ORIGINAL, IMAGEPATH_LARGEFANART, IMAGEPATH_LARGEFANART, IAMGEPATH_SMALLFANART, IMAGEPATH_ORIGINAL)
IMAGEPATH_QUALITY_THUMBS = (IMAGEPATH_ORIGINAL, IMAGEPATH_LARGEFANART, IAMGEPATH_SMALLFANART, IAMGEPATH_SMALLFANART, IMAGEPATH_ORIGINAL)
IMAGEPATH_QUALITY_CLOGOS = (IMAGEPATH_ORIGINAL, IMAGEPATH_LARGELOGO, IMAGEPATH_LARGELOGO, IMAGEPATH_SMALLLOGO, IMAGEPATH_ORIGINAL)
IMAGEPATH_ASPECTRATIO = ('other', 'poster', 'square', 'thumb', 'landscape', 'wide')

PLAYERS_URLENCODE = (
    'name', 'showname', 'clearname', 'tvshowtitle', 'title', 'thumbnail', 'poster', 'fanart',
    'originaltitle', 'plot', 'cast', 'actors')

PLAYERS_BASEDIR_USER = 'special://profile/addon_data/plugin.video.themoviedb.helper/players/'
PLAYERS_BASEDIR_SAVE = 'special://profile/addon_data/plugin.video.themoviedb.helper/reconfigured_players/'
PLAYERS_BASEDIR_BUNDLED = 'special://home/addons/plugin.video.themoviedb.helper/resources/players/'
PLAYERS_BASEDIR_TEMPLATES = 'special://home/addons/plugin.video.themoviedb.helper/resources/templates/'
PLAYERS_PRIORITY = 1000
PLAYERS_REQUIRED_IDS = ('{imdb}', '{tvdb}', '{trakt}', '{slug}', '{eptvdb}' '{epimdb}', '{eptrakt}', '{epslug}', '{epid}')
PLAYERS_CHOSEN_DEFAULTS_FILENAME = 'player_defaults'

NO_UNAIRED_LABEL = ('details', 'trakt_calendar', 'library_nextaired', 'videos', 'trakt_watchlist_anticipated', 'trakt_anticipated')

PARAM_WIDGETS_RELOAD = 'reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]'
PARAM_WIDGETS_RELOAD_FORCED = 'reload=$INFO[System.Time(hh:mm:ss)]'

LASTACTIVITIES_DATA = 'TraktNewSyncLastActivities'

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

RANDOMISED_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.items.directories.lists_random',
    'import_attr': 'ListRandom'}
RANDOMISED_LISTS = {
    'random_genres': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
            'import_attr': 'ListRandomGenre'
        }
    },
    'random_providers': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
            'import_attr': 'ListRandomProvider'
        }
    },
    'random_keywords': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
            'import_attr': 'ListRandomKeyword'
        }
    },
    'random_networks': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
            'import_attr': 'ListRandomNetwork'
        }
    },
    'random_studios': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
            'import_attr': 'ListRandomStudio'
        }
    },

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

RANDOMISED_TRAKT = {
    'random_trending': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktTrendingRandomised'
        }
    },
    'random_popular': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktPopularRandomised'
        }
    },
    'random_mostplayed': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktMostPlayedRandomised'
        }
    },
    'random_mostviewers': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktMostWatchedRandomised'
        }
    },
    'random_anticipated': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktAnticipatedRandomised'
        }
    }}

TMDB_BASIC_LISTS = {
    'popular': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListPopular'
        },
    },
    'top_rated': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListTopRated'
        },
    },
    'upcoming': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListUpcoming'
        },
    },
    'trending_day': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListTrendingDay'
        },
    },
    'trending_week': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListTrendingWeek'
        },
    },
    'now_playing': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListInTheatres'
        },
    },
    'airing_today': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListAiringToday'
        },
    },
    'on_the_air': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListCurrentlyAiring'
        },
    },
    'revenue_movies': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListRevenue'
        },
    },
    'most_voted': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
            'import_attr': 'ListMostVoted'
        },
    },
    'recommendations': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
            'import_attr': 'ListRecommendations'
        },
    },
    'similar': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
            'import_attr': 'ListSimilar'
        },
    },
    'reviews': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
            'import_attr': 'ListReviews'
        },
    },
    'movie_keywords': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
            'import_attr': 'ListKeywords'
        },
    },
    'genres': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListGenres'
        },
    },
    'watch_providers': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListProviders'
        },
    },
    'all_studios': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListStudios'
        },
    },
    'all_networks': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListNetworks'
        },
    },
    'all_collections': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListCollections'
        },
    },
    'all_keywords': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListKeywords'
        },
    },
    'all_movies': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListMovies'
        },
    },
    'all_tvshows': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view',
            'import_attr': 'ListTvshows'
        },
    },
    'tmdb_v4_recommendations': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListRecommendations'
        },
    },
    'tmdb_v4_favorites': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListFavourites'
        },
    },
    'tmdb_v4_watchlist': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListWatchlist'
        },
    },
    'tmdb_v4_rated': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListRated'
        },
    },
    'tmdb_v4_list': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListList'
        },
    },
    'tmdb_v4_lists': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
            'import_attr': 'ListLists'
        },
    },
}


TRAKT_BASIC_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
    'import_attr': 'ListBasic'}
TRAKT_BASIC_LISTS = {
    'trakt_trending': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktTrending'
        }
    },
    'trakt_popular': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktPopular'
        }
    },
    'trakt_mostplayed': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktMostPlayed'
        }
    },
    'trakt_mostviewers': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktMostWatched'
        }
    },
    'trakt_anticipated': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktAnticipated'
        }
    },
    'trakt_boxoffice': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktBoxOffice'
        }
    },
    'trakt_recommendations': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktRecommendations'
        }
    },
    'trakt_myairing': {
        'route': {
            'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
            'import_attr': 'ListTraktMyCalendars'
        }
    },
}


TRAKT_LIST_OF_LISTS_ROUTE = {
    'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
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
    'module_name': 'tmdbhelper.lib.items.directories.lists_mdblist',
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
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_search',
        'import_attr': 'ListSearchDir'}},
    'dir_multisearch': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_search',
        'import_attr': 'ListMultiSearchDir'}},
    'search': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_search',
        'import_attr': 'ListSearch'}},
    'dir_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListDiscoverDir'}},
    'discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListDiscover'}},
    'user_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListUserDiscover'}},
    'trakt_towatch': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListToWatch'}},
    'trakt_becauseyouwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListRandomBecauseYouWatched'}},
    'trakt_becausemostwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListRandomBecauseYouWatched'}},
    'trakt_calendar': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListCalendar'}},
    'library_nextaired': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListLibraryCalendar'}},
    'library_airingnext': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_airingnext',
        'import_attr': 'ListLibraryAiringNext'}},
    'trakt_airingnext': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_airingnext',
        'import_attr': 'ListTraktAiringNext'}},
    'trakt_collection': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListCollection'}},
    'trakt_watchlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListWatchlist'}},
    'trakt_watchlist_released': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListWatchlistReleased'}},
    'trakt_watchlist_anticipated': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListWatchlistAnticipated'}},
    'trakt_history': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListHistory'}},
    'trakt_mostwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListMostWatched'}},
    'trakt_favorites': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListFavorites'}},
    'trakt_dropped': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListDropped'}},
    'trakt_inprogress': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListInProgress'}},
    'trakt_ondeck': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListOnDeck'}},
    'trakt_ondeck_unwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListOnDeckUnWatched'}},
    'trakt_nextepisodes': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListNextEpisodes'}},
    'trakt_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListCustom'}},
    'trakt_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListCustomSearch'}},
    'trakt_sortby': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListSortBy'}},
    'trakt_comments': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListComments'}},
    'trakt_genres': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_trakt',
        'import_attr': 'ListGenres'}},
    'mdblist_locallist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_mdblist',
        'import_attr': 'ListLocal'}},
    'mdblist_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_mdblist',
        'import_attr': 'ListCustom'}},
    'mdblist_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_mdblist',
        'import_attr': 'ListCustomSearch'}},
    'dir_tvdb_awards': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tvdb.lists_awards',
        'import_attr': 'ListAwards'}},
    'dir_tvdb_award_categories': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tvdb.lists_awards',
        'import_attr': 'ListAwardCategories'}},
    'tvdb_award_category': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tvdb.lists_awards',
        'import_attr': 'ListAwardCategory'}},
    'dir_tvdb_genres': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tvdb.lists_genres',
        'import_attr': 'ListGenres'}},
    'tvdb_genre': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tvdb.lists_genres',
        'import_attr': 'ListGenre'}},
}


ROUTE_TMDBID = {
    'details': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_base',
        'import_attr': 'ListDetails'}},
    'fanart': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListFanart'}},
    'posters': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListPoster'}},
    'images': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListImage'}},
    'episode_thumbs': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListThumb'}},
    'cast': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCast'}},
    'crew': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCrew'}},
    'collection': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListSeries'}},
    'stars_in_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListStarredMovies'}},
    'stars_in_tvshows': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListStarredTvshows'}},
    'stars_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListStarredCombined'}},
    'crew_in_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCrewedMovies'}},
    'crew_in_tvshows': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCrewedTvshows'}},
    'crew_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCrewedCombined'}},
    'credits_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListCreditsCombined'}},
    'videos': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.lists_view',
        'import_attr': 'ListVideos'}},
    'seasons': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListSeasons'}},
    'flatseasons': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListFlatSeasons'}},
    'anticipated_episodes': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListAnticipatedEpisodes'}},
    'episodes': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListEpisodes'}},
    'next_recommendation': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_nextup',
        'import_attr': 'ListNextRecommendation'}},
    'trakt_upnext': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListUpNext'}},
}
