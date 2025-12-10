CACHE_SHORT, CACHE_MEDIUM, CACHE_LONG, CACHE_EXTENDED = 1, 7, 14, 90
ITER_PROPS_MAX = 10

DAY_IN_SECONDS = 86400
DEFAULT_EXPIRY = DAY_IN_SECONDS * 30
SHORTER_EXPIRY = DAY_IN_SECONDS * 7
TEMPDAY_EXPIRY = DAY_IN_SECONDS
HALFDAY_EXPIRY = DAY_IN_SECONDS * 0.5

DATALEVEL_MIN = 1
DATALEVEL_MAX = 5
SQLITE_FALSE = 0
SQLITE_TRUE = 1

TVDB_DISCLAIMER = 'Information provided by TheTVDB.com. Please consider supporting them. https://thetvdb.com/subscribe'

NODE_BASEDIR = 'special://profile/addon_data/plugin.video.themoviedb.helper/nodes/'
RUNSCRIPT = 'Runscript(plugin.video.themoviedb.helper,{})'

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
PLAYERS_CHOSEN_DEFAULTS_FILENAME = 'player_defaults'

NO_UNAIRED_LABEL = ('details', 'trakt_calendar', 'library_nextaired', 'videos', 'trakt_watchlist_anticipated', 'trakt_anticipated')

PARAM_WIDGETS_RELOAD = 'reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]'
PARAM_WIDGETS_RELOAD_FORCED = 'reload=$INFO[System.Time(hh:mm:ss)]'

LASTACTIVITIES_DATA = 'TraktNewSyncLastActivities'
LASTACTIVITIES_EXPIRY = 600

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
    'gemini': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_gemini',
        'import_attr': 'ListGemini'}},
    'dir_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListDiscoverDir'}},
    'discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListDiscover'}},
    'user_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListUserDiscover'}},

    'dir_tmdb_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_new_discover',
        'import_attr': 'ListDiscoverDir'}},
    'tmdb_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_new_discover',
        'import_attr': 'ListDiscover'}},

    'dir_trakt_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_discover',
        'import_attr': 'ListDiscoverDir'}},
    'trakt_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_discover',
        'import_attr': 'ListDiscover'}},
    'trakt_towatch': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListToWatch'}},
    'trakt_becauseyouwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListRandomBecauseYouWatched'}},
    'trakt_becausemostwatched': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListRandomBecauseYouWatched'}},
    'library_nextaired': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_calendar',
        'import_attr': 'ListLocalCalendar'}},
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
    'trakt_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticSearch'}},
    'trakt_trendinglists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticTrending'}},
    'trakt_popularlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticPopular'}},
    'trakt_likedlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticLiked'}},
    'trakt_mylists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticOwned'}},
    'trakt_inlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticListed'}},
    'trakt_userslists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticUsers'}},
    'trakt_trending': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_filtered',
        'import_attr': 'ListTraktTrending'}},
    'trakt_popular': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_filtered',
        'import_attr': 'ListTraktPopular'}},
    'trakt_mostplayed': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_filtered',
        'import_attr': 'ListTraktMostPlayed'}},
    'trakt_mostviewers': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_filtered',
        'import_attr': 'ListTraktMostWatched'}},
    'trakt_anticipated': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_filtered',
        'import_attr': 'ListTraktAnticipated'}},
    'trakt_myairing': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_calendar',
        'import_attr': 'ListTraktMyAiring'}},
    'trakt_calendar': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_calendar',
        'import_attr': 'ListTraktCalendar'}},
    'trakt_moviecalendar': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_calendar',
        'import_attr': 'ListTraktMoviesCalendar'}},
    'trakt_dvdcalendar': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_calendar',
        'import_attr': 'ListTraktDVDsCalendar'}},
    'trakt_boxoffice': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
        'import_attr': 'ListTraktBoxOffice'}},
    'trakt_recommendations': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_standard',
        'import_attr': 'ListTraktRecommendations'}},
    'trakt_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_custom',
        'import_attr': 'ListTraktCustom'}},
    'trakt_sortby': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sorting',
        'import_attr': 'ListTraktSortBy'}},
    'trakt_genres': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_static',
        'import_attr': 'ListTraktStaticGenres'}},
    'trakt_years': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_years',
        'import_attr': 'ListTraktYears'}},
    'mdblist_sortby': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_sorting',
        'import_attr': 'ListMDbListSortBy'}},
    'mdblist_locallist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_local',
        'import_attr': 'ListMDbListLocal'}},
    'mdblist_userlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_custom',
        'import_attr': 'ListMDbListCustom'}},
    'mdblist_toplists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_lists',
        'import_attr': 'ListMDbListListsTop'}},
    'mdblist_yourlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_lists',
        'import_attr': 'ListMDbListListsUser'}},
    'mdblist_searchlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.mdblist.lists_lists',
        'import_attr': 'ListMDbListListsSearch'}},
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
    'popular': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListPopular'}},
    'top_rated': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListTopRated'}},
    'upcoming': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListUpcoming'}},
    'trending_day': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListTrendingDay'}},
    'trending_week': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListTrendingWeek'}},
    'now_playing': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListInTheatres'}},
    'airing_today': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListAiringToday'}},
    'on_the_air': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListCurrentlyAiring'}},
    'revenue_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListRevenue'}},
    'most_voted': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_standard',
        'import_attr': 'ListMostVoted'}},
    'genres': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListGenres'}},
    'watch_providers': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListProviders'}},
    'all_studios': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListStudios'}},
    'all_networks': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListNetworks'}},
    'all_collections': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListCollections'}},
    'all_keywords': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListKeywords'}},
    'all_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListMovies'}},
    'all_tvshows': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_allitems',
        'import_attr': 'ListTvshows'}},
    'tmdb_v4_recommendations': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListRecommendations'}},
    'tmdb_v4_favorites': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListFavourites'}},
    'tmdb_v4_watchlist': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListWatchlist'}},
    'tmdb_v4_rated': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListRated'}},
    'tmdb_v4_list': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListList'}},
    'tmdb_v4_lists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_authenticated',
        'import_attr': 'ListLists'}},
    'random_genres': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
        'import_attr': 'ListRandomGenre'}},
    'random_providers': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
        'import_attr': 'ListRandomProvider'}},
    'random_keywords': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
        'import_attr': 'ListRandomKeyword'}},
    'random_networks': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
        'import_attr': 'ListRandomNetwork'}},
    'random_studios': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_random',
        'import_attr': 'ListRandomStudio'}},
    'random_trendinglists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktStaticTrendingRandomised'}},
    'random_popularlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktStaticPopularRandomised'}},
    'random_likedlists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktStaticLikedRandomised'}},
    'random_mylists': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktStaticOwnedRandomised'}},
    'random_trending': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktTrendingRandomised'}},
    'random_popular': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktPopularRandomised'}},
    'random_mostplayed': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktMostPlayedRandomised'}},
    'random_mostviewers': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktMostWatchedRandomised'}},
    'random_anticipated': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_random',
        'import_attr': 'ListTraktAnticipatedRandomised'}},
}


ROUTE_TMDBID = {
    'details': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.base.lists_details',
        'import_attr': 'ListDetails'}},
    'fanart': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListFanart'}},
    'posters': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListPoster'}},
    'images': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListImage'}},
    'episode_thumbs': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListThumb'}},
    'cast': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCast'}},
    'crew': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCrew'}},
    'collection': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListSeries'}},
    'stars_in_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListStarredMovies'}},
    'stars_in_tvshows': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListStarredTvshows'}},
    'stars_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListStarredCombined'}},
    'crew_in_movies': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCrewedMovies'}},
    'crew_in_tvshows': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCrewedTvshows'}},
    'crew_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCrewedCombined'}},
    'credits_in_both': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
        'import_attr': 'ListCreditsCombined'}},
    'videos': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_view_db',
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
    'specified_episodes': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListSpecifiedEpisodes'}},
    'episodes': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_seasons',
        'import_attr': 'ListEpisodes'}},
    'next_recommendation': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_nextup',
        'import_attr': 'ListNextRecommendation'}},
    'trakt_upnext': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_sync',
        'import_attr': 'ListUpNext'}},
    'trakt_related': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_related',
        'import_attr': 'ListTraktRelated'}},
    'trakt_comments': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_related',
        'import_attr': 'ListTraktComments'}},
    'trakt_watchers': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.trakt.lists_related',
        'import_attr': 'ListTraktWatchers'}},
    'recommendations': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
        'import_attr': 'ListRecommendations'}},
    'similar': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
        'import_attr': 'ListSimilar'}},
    'reviews': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
        'import_attr': 'ListReviews'}},
    'movie_keywords': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_related',
        'import_attr': 'ListKeywords'}},
}


"""
DISCOVER
"""

DISCOVER_REGIONS = (
    {'id': 'AD', 'name': u'Andorra (AD)'},
    {'id': 'AE', 'name': u'United Arab Emirates (AE)'},
    {'id': 'AF', 'name': u'Afghanistan (AF)'},
    {'id': 'AG', 'name': u'Antigua and Barbuda (AG)'},
    {'id': 'AI', 'name': u'Anguilla (AI)'},
    {'id': 'AL', 'name': u'Albania (AL)'},
    {'id': 'AM', 'name': u'Armenia (AM)'},
    {'id': 'AO', 'name': u'Angola (AO)'},
    {'id': 'AQ', 'name': u'Antarctica (AQ)'},
    {'id': 'AR', 'name': u'Argentina (AR)'},
    {'id': 'AS', 'name': u'American Samoa (AS)'},
    {'id': 'AT', 'name': u'Austria (AT)'},
    {'id': 'AU', 'name': u'Australia (AU)'},
    {'id': 'AW', 'name': u'Aruba (AW)'},
    {'id': 'AX', 'name': u'Åland Islands (AX)'},
    {'id': 'AZ', 'name': u'Azerbaijan (AZ)'},
    {'id': 'BA', 'name': u'Bosnia and Herzegovina (BA)'},
    {'id': 'BB', 'name': u'Barbados (BB)'},
    {'id': 'BD', 'name': u'Bangladesh (BD)'},
    {'id': 'BE', 'name': u'Belgium (BE)'},
    {'id': 'BF', 'name': u'Burkina Faso (BF)'},
    {'id': 'BG', 'name': u'Bulgaria (BG)'},
    {'id': 'BH', 'name': u'Bahrain (BH)'},
    {'id': 'BI', 'name': u'Burundi (BI)'},
    {'id': 'BJ', 'name': u'Benin (BJ)'},
    {'id': 'BL', 'name': u'Saint Barthélemy (BL)'},
    {'id': 'BM', 'name': u'Bermuda (BM)'},
    {'id': 'BN', 'name': u'Brunei Darussalam (BN)'},
    {'id': 'BO', 'name': u'Bolivia (BO)'},
    {'id': 'BQ', 'name': u'Bonaire (BQ)'},
    {'id': 'BR', 'name': u'Brazil (BR)'},
    {'id': 'BS', 'name': u'Bahamas (BS)'},
    {'id': 'BT', 'name': u'Bhutan (BT)'},
    {'id': 'BV', 'name': u'Bouvet Island (BV)'},
    {'id': 'BW', 'name': u'Botswana (BW)'},
    {'id': 'BY', 'name': u'Belarus (BY)'},
    {'id': 'BZ', 'name': u'Belize (BZ)'},
    {'id': 'CA', 'name': u'Canada (CA)'},
    {'id': 'CC', 'name': u'Cocos (CC)'},
    {'id': 'CD', 'name': u'Congo (CD)'},
    {'id': 'CF', 'name': u'Central African Republic (CF)'},
    {'id': 'CG', 'name': u'Congo (CG)'},
    {'id': 'CH', 'name': u'Switzerland (CH)'},
    {'id': 'CI', 'name': u'Côte d\'Ivoire (CI)'},
    {'id': 'CK', 'name': u'Cook Islands (CK)'},
    {'id': 'CL', 'name': u'Chile (CL)'},
    {'id': 'CM', 'name': u'Cameroon (CM)'},
    {'id': 'CN', 'name': u'China (CN)'},
    {'id': 'CO', 'name': u'Colombia (CO)'},
    {'id': 'CR', 'name': u'Costa Rica (CR)'},
    {'id': 'CU', 'name': u'Cuba (CU)'},
    {'id': 'CV', 'name': u'Cabo Verde (CV)'},
    {'id': 'CW', 'name': u'Curaçao (CW)'},
    {'id': 'CX', 'name': u'Christmas Island (CX)'},
    {'id': 'CY', 'name': u'Cyprus (CY)'},
    {'id': 'CZ', 'name': u'Czechia (CZ)'},
    {'id': 'DE', 'name': u'Germany (DE)'},
    {'id': 'DJ', 'name': u'Djibouti (DJ)'},
    {'id': 'DK', 'name': u'Denmark (DK)'},
    {'id': 'DM', 'name': u'Dominica (DM)'},
    {'id': 'DO', 'name': u'Dominican Republic (DO)'},
    {'id': 'DZ', 'name': u'Algeria (DZ)'},
    {'id': 'EC', 'name': u'Ecuador (EC)'},
    {'id': 'EE', 'name': u'Estonia (EE)'},
    {'id': 'EG', 'name': u'Egypt (EG)'},
    {'id': 'EH', 'name': u'Western Sahara (EH)'},
    {'id': 'ER', 'name': u'Eritrea (ER)'},
    {'id': 'ES', 'name': u'Spain (ES)'},
    {'id': 'ET', 'name': u'Ethiopia (ET)'},
    {'id': 'FI', 'name': u'Finland (FI)'},
    {'id': 'FJ', 'name': u'Fiji (FJ)'},
    {'id': 'FK', 'name': u'Falkland Islands (FK)'},
    {'id': 'FM', 'name': u'Micronesia (FM)'},
    {'id': 'FO', 'name': u'Faroe Islands (FO)'},
    {'id': 'FR', 'name': u'France (FR)'},
    {'id': 'GA', 'name': u'Gabon (GA)'},
    {'id': 'GB', 'name': u'United Kingdom (GB)'},
    {'id': 'GD', 'name': u'Grenada (GD)'},
    {'id': 'GE', 'name': u'Georgia (GE)'},
    {'id': 'GF', 'name': u'French Guiana (GF)'},
    {'id': 'GG', 'name': u'Guernsey (GG)'},
    {'id': 'GH', 'name': u'Ghana (GH)'},
    {'id': 'GI', 'name': u'Gibraltar (GI)'},
    {'id': 'GL', 'name': u'Greenland (GL)'},
    {'id': 'GM', 'name': u'Gambia (GM)'},
    {'id': 'GN', 'name': u'Guinea (GN)'},
    {'id': 'GP', 'name': u'Guadeloupe (GP)'},
    {'id': 'GQ', 'name': u'Equatorial Guinea (GQ)'},
    {'id': 'GR', 'name': u'Greece (GR)'},
    {'id': 'GS', 'name': u'South Georgia and the South Sandwich Islands (GS)'},
    {'id': 'GT', 'name': u'Guatemala (GT)'},
    {'id': 'GU', 'name': u'Guam (GU)'},
    {'id': 'GW', 'name': u'Guinea-Bissau (GW)'},
    {'id': 'GY', 'name': u'Guyana (GY)'},
    {'id': 'HK', 'name': u'Hong Kong (HK)'},
    {'id': 'HM', 'name': u'Heard Island and McDonald Islands (HM)'},
    {'id': 'HN', 'name': u'Honduras (HN)'},
    {'id': 'HR', 'name': u'Croatia (HR)'},
    {'id': 'HT', 'name': u'Haiti (HT)'},
    {'id': 'HU', 'name': u'Hungary (HU)'},
    {'id': 'ID', 'name': u'Indonesia (ID)'},
    {'id': 'IE', 'name': u'Ireland (IE)'},
    {'id': 'IL', 'name': u'Israel (IL)'},
    {'id': 'IM', 'name': u'Isle of Man (IM)'},
    {'id': 'IN', 'name': u'India (IN)'},
    {'id': 'IO', 'name': u'British Indian Ocean Territory (IO)'},
    {'id': 'IQ', 'name': u'Iraq (IQ)'},
    {'id': 'IR', 'name': u'Iran (IR)'},
    {'id': 'IS', 'name': u'Iceland (IS)'},
    {'id': 'IT', 'name': u'Italy (IT)'},
    {'id': 'JE', 'name': u'Jersey (JE)'},
    {'id': 'JM', 'name': u'Jamaica (JM)'},
    {'id': 'JO', 'name': u'Jordan (JO)'},
    {'id': 'JP', 'name': u'Japan (JP)'},
    {'id': 'KE', 'name': u'Kenya (KE)'},
    {'id': 'KG', 'name': u'Kyrgyzstan (KG)'},
    {'id': 'KH', 'name': u'Cambodia (KH)'},
    {'id': 'KI', 'name': u'Kiribati (KI)'},
    {'id': 'KM', 'name': u'Comoros (KM)'},
    {'id': 'KN', 'name': u'Saint Kitts and Nevis (KN)'},
    {'id': 'KP', 'name': u'Korea (KP)'},
    {'id': 'KR', 'name': u'Korea (KR)'},
    {'id': 'KW', 'name': u'Kuwait (KW)'},
    {'id': 'KY', 'name': u'Cayman Islands (KY)'},
    {'id': 'KZ', 'name': u'Kazakhstan (KZ)'},
    {'id': 'LA', 'name': u'Lao People\'s Democratic Republic (LA)'},
    {'id': 'LB', 'name': u'Lebanon (LB)'},
    {'id': 'LC', 'name': u'Saint Lucia (LC)'},
    {'id': 'LI', 'name': u'Liechtenstein (LI)'},
    {'id': 'LK', 'name': u'Sri Lanka (LK)'},
    {'id': 'LR', 'name': u'Liberia (LR)'},
    {'id': 'LS', 'name': u'Lesotho (LS)'},
    {'id': 'LT', 'name': u'Lithuania (LT)'},
    {'id': 'LU', 'name': u'Luxembourg (LU)'},
    {'id': 'LV', 'name': u'Latvia (LV)'},
    {'id': 'LY', 'name': u'Libya (LY)'},
    {'id': 'MA', 'name': u'Morocco (MA)'},
    {'id': 'MC', 'name': u'Monaco (MC)'},
    {'id': 'MD', 'name': u'Moldova (MD)'},
    {'id': 'ME', 'name': u'Montenegro (ME)'},
    {'id': 'MF', 'name': u'Saint Martin (MF)'},
    {'id': 'MG', 'name': u'Madagascar (MG)'},
    {'id': 'MH', 'name': u'Marshall Islands (MH)'},
    {'id': 'MK', 'name': u'North Macedonia (MK)'},
    {'id': 'ML', 'name': u'Mali (ML)'},
    {'id': 'MM', 'name': u'Myanmar (MM)'},
    {'id': 'MN', 'name': u'Mongolia (MN)'},
    {'id': 'MO', 'name': u'Macao (MO)'},
    {'id': 'MP', 'name': u'Northern Mariana Islands (MP)'},
    {'id': 'MQ', 'name': u'Martinique (MQ)'},
    {'id': 'MR', 'name': u'Mauritania (MR)'},
    {'id': 'MS', 'name': u'Montserrat (MS)'},
    {'id': 'MT', 'name': u'Malta (MT)'},
    {'id': 'MU', 'name': u'Mauritius (MU)'},
    {'id': 'MV', 'name': u'Maldives (MV)'},
    {'id': 'MW', 'name': u'Malawi (MW)'},
    {'id': 'MX', 'name': u'Mexico (MX)'},
    {'id': 'MY', 'name': u'Malaysia (MY)'},
    {'id': 'MZ', 'name': u'Mozambique (MZ)'},
    {'id': 'NA', 'name': u'Namibia (NA)'},
    {'id': 'NC', 'name': u'New Caledonia (NC)'},
    {'id': 'NE', 'name': u'Niger (NE)'},
    {'id': 'NF', 'name': u'Norfolk Island (NF)'},
    {'id': 'NG', 'name': u'Nigeria (NG)'},
    {'id': 'NI', 'name': u'Nicaragua (NI)'},
    {'id': 'NL', 'name': u'Netherlands (NL)'},
    {'id': 'NO', 'name': u'Norway (NO)'},
    {'id': 'NP', 'name': u'Nepal (NP)'},
    {'id': 'NR', 'name': u'Nauru (NR)'},
    {'id': 'NU', 'name': u'Niue (NU)'},
    {'id': 'NZ', 'name': u'New Zealand (NZ)'},
    {'id': 'OM', 'name': u'Oman (OM)'},
    {'id': 'PA', 'name': u'Panama (PA)'},
    {'id': 'PE', 'name': u'Peru (PE)'},
    {'id': 'PF', 'name': u'French Polynesia (PF)'},
    {'id': 'PG', 'name': u'Papua New Guinea (PG)'},
    {'id': 'PH', 'name': u'Philippines (PH)'},
    {'id': 'PK', 'name': u'Pakistan (PK)'},
    {'id': 'PL', 'name': u'Poland (PL)'},
    {'id': 'PM', 'name': u'Saint Pierre and Miquelon (PM)'},
    {'id': 'PN', 'name': u'Pitcairn (PN)'},
    {'id': 'PR', 'name': u'Puerto Rico (PR)'},
    {'id': 'PS', 'name': u'Palestine (PS)'},
    {'id': 'PT', 'name': u'Portugal (PT)'},
    {'id': 'PW', 'name': u'Palau (PW)'},
    {'id': 'PY', 'name': u'Paraguay (PY)'},
    {'id': 'QA', 'name': u'Qatar (QA)'},
    {'id': 'RE', 'name': u'Réunion (RE)'},
    {'id': 'RO', 'name': u'Romania (RO)'},
    {'id': 'RS', 'name': u'Serbia (RS)'},
    {'id': 'RU', 'name': u'Russian Federation (RU)'},
    {'id': 'RW', 'name': u'Rwanda (RW)'},
    {'id': 'SA', 'name': u'Saudi Arabia (SA)'},
    {'id': 'SB', 'name': u'Solomon Islands (SB)'},
    {'id': 'SC', 'name': u'Seychelles (SC)'},
    {'id': 'SD', 'name': u'Sudan (SD)'},
    {'id': 'SE', 'name': u'Sweden (SE)'},
    {'id': 'SG', 'name': u'Singapore (SG)'},
    {'id': 'SH', 'name': u'Saint Helena (SH)'},
    {'id': 'SI', 'name': u'Slovenia (SI)'},
    {'id': 'SJ', 'name': u'Svalbard and Jan Mayen (SJ)'},
    {'id': 'SK', 'name': u'Slovakia (SK)'},
    {'id': 'SL', 'name': u'Sierra Leone (SL)'},
    {'id': 'SM', 'name': u'San Marino (SM)'},
    {'id': 'SN', 'name': u'Senegal (SN)'},
    {'id': 'SO', 'name': u'Somalia (SO)'},
    {'id': 'SR', 'name': u'Suriname (SR)'},
    {'id': 'SS', 'name': u'South Sudan (SS)'},
    {'id': 'ST', 'name': u'Sao Tome and Principe (ST)'},
    {'id': 'SV', 'name': u'El Salvador (SV)'},
    {'id': 'SX', 'name': u'Sint Maarten (SX)'},
    {'id': 'SY', 'name': u'Syrian Arab Republic (SY)'},
    {'id': 'SZ', 'name': u'Eswatini (SZ)'},
    {'id': 'TC', 'name': u'Turks and Caicos Islands (TC)'},
    {'id': 'TD', 'name': u'Chad (TD)'},
    {'id': 'TF', 'name': u'French Southern Territories (TF)'},
    {'id': 'TG', 'name': u'Togo (TG)'},
    {'id': 'TH', 'name': u'Thailand (TH)'},
    {'id': 'TJ', 'name': u'Tajikistan (TJ)'},
    {'id': 'TK', 'name': u'Tokelau (TK)'},
    {'id': 'TL', 'name': u'Timor-Leste (TL)'},
    {'id': 'TM', 'name': u'Turkmenistan (TM)'},
    {'id': 'TN', 'name': u'Tunisia (TN)'},
    {'id': 'TO', 'name': u'Tonga (TO)'},
    {'id': 'TR', 'name': u'Turkey (TR)'},
    {'id': 'TT', 'name': u'Trinidad and Tobago (TT)'},
    {'id': 'TV', 'name': u'Tuvalu (TV)'},
    {'id': 'TW', 'name': u'Taiwan (TW)'},
    {'id': 'TZ', 'name': u'Tanzania (TZ)'},
    {'id': 'UA', 'name': u'Ukraine (UA)'},
    {'id': 'UG', 'name': u'Uganda (UG)'},
    {'id': 'US', 'name': u'United States of America (US)'},
    {'id': 'UY', 'name': u'Uruguay (UY)'},
    {'id': 'UZ', 'name': u'Uzbekistan (UZ)'},
    {'id': 'VA', 'name': u'Holy See (VA)'},
    {'id': 'VC', 'name': u'Saint Vincent and the Grenadines (VC)'},
    {'id': 'VE', 'name': u'Venezuela (VE)'},
    {'id': 'VG', 'name': u'Virgin Islands (VG)'},
    {'id': 'VI', 'name': u'Virgin Islands (VI)'},
    {'id': 'VN', 'name': u'Viet Nam (VN)'},
    {'id': 'VU', 'name': u'Vanuatu (VU)'},
    {'id': 'WF', 'name': u'Wallis and Futuna (WF)'},
    {'id': 'WS', 'name': u'Samoa (WS)'},
    {'id': 'YE', 'name': u'Yemen (YE)'},
    {'id': 'YT', 'name': u'Mayotte (YT)'},
    {'id': 'ZA', 'name': u'South Africa (ZA)'},
    {'id': 'ZM', 'name': u'Zambia (ZM)'},
    {'id': 'ZW', 'name': u'Zimbabwe (ZW)'}
)
