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
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discodir',
        'import_attr': 'ListDiscoverDir'}},
    'discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discover',
        'import_attr': 'ListDiscover'}},
    'user_discover': {'route': {
        'module_name': 'tmdbhelper.lib.items.directories.tmdb.lists_discodir',
        'import_attr': 'ListUserDiscover'}},
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

DISCOVER_LANGUAGES = (
    {"id": "ab", "name": u"Abkhaz (ab)"},
    {"id": "aa", "name": u"Afar (aa)"},
    {"id": "af", "name": u"Afrikaans (af)"},
    {"id": "ak", "name": u"Akan (ak)"},
    {"id": "sq", "name": u"Albanian (sq)"},
    {"id": "am", "name": u"Amharic (am)"},
    {"id": "ar", "name": u"Arabic (ar)"},
    {"id": "an", "name": u"Aragonese (an)"},
    {"id": "hy", "name": u"Armenian (hy)"},
    {"id": "as", "name": u"Assamese (as)"},
    {"id": "av", "name": u"Avaric (av)"},
    {"id": "ae", "name": u"Avestan (ae)"},
    {"id": "ay", "name": u"Aymara (ay)"},
    {"id": "az", "name": u"Azerbaijani (az)"},
    {"id": "bm", "name": u"Bambara (bm)"},
    {"id": "ba", "name": u"Bashkir (ba)"},
    {"id": "eu", "name": u"Basque (eu)"},
    {"id": "be", "name": u"Belarusian (be)"},
    {"id": "bn", "name": u"Bengali; Bangla (bn)"},
    {"id": "bh", "name": u"Bihari (bh)"},
    {"id": "bi", "name": u"Bislama (bi)"},
    {"id": "bs", "name": u"Bosnian (bs)"},
    {"id": "br", "name": u"Breton (br)"},
    {"id": "bg", "name": u"Bulgarian (bg)"},
    {"id": "my", "name": u"Burmese (my)"},
    {"id": "ca", "name": u"Catalan; Valencian (ca)"},
    {"id": "ch", "name": u"Chamorro (ch)"},
    {"id": "ce", "name": u"Chechen (ce)"},
    {"id": "ny", "name": u"Chichewa; Chewa; Nyanja (ny)"},
    {"id": "zh", "name": u"Chinese (zh)"},
    {"id": "cv", "name": u"Chuvash (cv)"},
    {"id": "kw", "name": u"Cornish (kw)"},
    {"id": "co", "name": u"Corsican (co)"},
    {"id": "cr", "name": u"Cree (cr)"},
    {"id": "hr", "name": u"Croatian (hr)"},
    {"id": "cs", "name": u"Czech (cs)"},
    {"id": "da", "name": u"Danish (da)"},
    {"id": "dv", "name": u"Divehi; Dhivehi; Maldivian; (dv)"},
    {"id": "nl", "name": u"Dutch (nl)"},
    {"id": "dz", "name": u"Dzongkha (dz)"},
    {"id": "en", "name": u"English (en)"},
    {"id": "eo", "name": u"Esperanto (eo)"},
    {"id": "et", "name": u"Estonian (et)"},
    {"id": "ee", "name": u"Ewe (ee)"},
    {"id": "fo", "name": u"Faroese (fo)"},
    {"id": "fj", "name": u"Fijian (fj)"},
    {"id": "fi", "name": u"Finnish (fi)"},
    {"id": "fr", "name": u"French (fr)"},
    {"id": "ff", "name": u"Fula; Fulah; Pulaar; Pular (ff)"},
    {"id": "gl", "name": u"Galician (gl)"},
    {"id": "ka", "name": u"Georgian (ka)"},
    {"id": "de", "name": u"German (de)"},
    {"id": "el", "name": u"Greek, Modern (el)"},
    {"id": "gn", "name": u"GuaranÃ­ (gn)"},
    {"id": "gu", "name": u"Gujarati (gu)"},
    {"id": "ht", "name": u"Haitian; Haitian Creole (ht)"},
    {"id": "ha", "name": u"Hausa (ha)"},
    {"id": "he", "name": u"Hebrew (modern) (he)"},
    {"id": "hz", "name": u"Herero (hz)"},
    {"id": "hi", "name": u"Hindi (hi)"},
    {"id": "ho", "name": u"Hiri Motu (ho)"},
    {"id": "hu", "name": u"Hungarian (hu)"},
    {"id": "ia", "name": u"Interlingua (ia)"},
    {"id": "id", "name": u"Indonesian (id)"},
    {"id": "ie", "name": u"Interlingue (ie)"},
    {"id": "ga", "name": u"Irish (ga)"},
    {"id": "ig", "name": u"Igbo (ig)"},
    {"id": "ik", "name": u"Inupiaq (ik)"},
    {"id": "io", "name": u"Ido (io)"},
    {"id": "is", "name": u"Icelandic (is)"},
    {"id": "it", "name": u"Italian (it)"},
    {"id": "iu", "name": u"Inuktitut (iu)"},
    {"id": "ja", "name": u"Japanese (ja)"},
    {"id": "jv", "name": u"Javanese (jv)"},
    {"id": "kl", "name": u"Kalaallisut, Greenlandic (kl)"},
    {"id": "kn", "name": u"Kannada (kn)"},
    {"id": "kr", "name": u"Kanuri (kr)"},
    {"id": "ks", "name": u"Kashmiri (ks)"},
    {"id": "kk", "name": u"Kazakh (kk)"},
    {"id": "km", "name": u"Khmer (km)"},
    {"id": "ki", "name": u"Kikuyu, Gikuyu (ki)"},
    {"id": "rw", "name": u"Kinyarwanda (rw)"},
    {"id": "ky", "name": u"Kyrgyz (ky)"},
    {"id": "kv", "name": u"Komi (kv)"},
    {"id": "kg", "name": u"Kongo (kg)"},
    {"id": "ko", "name": u"Korean (ko)"},
    {"id": "ku", "name": u"Kurdish (ku)"},
    {"id": "kj", "name": u"Kwanyama, Kuanyama (kj)"},
    {"id": "la", "name": u"Latin (la)"},
    {"id": "lb", "name": u"Luxembourgish, Letzeburgesch (lb)"},
    {"id": "lg", "name": u"Ganda (lg)"},
    {"id": "li", "name": u"Limburgish, Limburgan, Limburger (li)"},
    {"id": "ln", "name": u"Lingala (ln)"},
    {"id": "lo", "name": u"Lao (lo)"},
    {"id": "lt", "name": u"Lithuanian (lt)"},
    {"id": "lu", "name": u"Luba-Katanga (lu)"},
    {"id": "lv", "name": u"Latvian (lv)"},
    {"id": "gv", "name": u"Manx (gv)"},
    {"id": "mk", "name": u"Macedonian (mk)"},
    {"id": "mg", "name": u"Malagasy (mg)"},
    {"id": "ms", "name": u"Malay (ms)"},
    {"id": "ml", "name": u"Malayalam (ml)"},
    {"id": "mt", "name": u"Maltese (mt)"},
    {"id": "mi", "name": u"MÄori (mi)"},
    {"id": "mr", "name": u"Marathi (MarÄá¹­hÄ«) (mr)"},
    {"id": "mh", "name": u"Marshallese (mh)"},
    {"id": "mn", "name": u"Mongolian (mn)"},
    {"id": "na", "name": u"Nauru (na)"},
    {"id": "nv", "name": u"Navajo, Navaho (nv)"},
    {"id": "nb", "name": u"Norwegian BokmÃ¥l (nb)"},
    {"id": "nd", "name": u"North Ndebele (nd)"},
    {"id": "ne", "name": u"Nepali (ne)"},
    {"id": "ng", "name": u"Ndonga (ng)"},
    {"id": "nn", "name": u"Norwegian Nynorsk (nn)"},
    {"id": "no", "name": u"Norwegian (no)"},
    {"id": "ii", "name": u"Nuosu (ii)"},
    {"id": "nr", "name": u"South Ndebele (nr)"},
    {"id": "oc", "name": u"Occitan (oc)"},
    {"id": "oj", "name": u"Ojibwe, Ojibwa (oj)"},
    {"id": "cu", "name": u"Old Church Slavonic, Church Slavic, Church Slavonic, Old Bulgarian, Old Slavonic (cu)"},
    {"id": "om", "name": u"Oromo (om)"},
    {"id": "or", "name": u"Oriya (or)"},
    {"id": "os", "name": u"Ossetian, Ossetic (os)"},
    {"id": "pa", "name": u"Panjabi, Punjabi (pa)"},
    {"id": "pi", "name": u"PÄli (pi)"},
    {"id": "fa", "name": u"Persian (Farsi) (fa)"},
    {"id": "pl", "name": u"Polish (pl)"},
    {"id": "ps", "name": u"Pashto, Pushto (ps)"},
    {"id": "pt", "name": u"Portuguese (pt)"},
    {"id": "qu", "name": u"Quechua (qu)"},
    {"id": "rm", "name": u"Romansh (rm)"},
    {"id": "rn", "name": u"Kirundi (rn)"},
    {"id": "ro", "name": u"Romanian, []) (ro)"},
    {"id": "ru", "name": u"Russian (ru)"},
    {"id": "sa", "name": u"Sanskrit (Saá¹ská¹›ta) (sa)"},
    {"id": "sc", "name": u"Sardinian (sc)"},
    {"id": "sd", "name": u"Sindhi (sd)"},
    {"id": "se", "name": u"Northern Sami (se)"},
    {"id": "sm", "name": u"Samoan (sm)"},
    {"id": "sg", "name": u"Sango (sg)"},
    {"id": "sr", "name": u"Serbian (sr)"},
    {"id": "gd", "name": u"Scottish Gaelic; Gaelic (gd)"},
    {"id": "sn", "name": u"Shona (sn)"},
    {"id": "si", "name": u"Sinhala, Sinhalese (si)"},
    {"id": "sk", "name": u"Slovak (sk)"},
    {"id": "sl", "name": u"Slovene (sl)"},
    {"id": "so", "name": u"Somali (so)"},
    {"id": "st", "name": u"Southern Sotho (st)"},
    {"id": "az", "name": u"South Azerbaijani (az)"},
    {"id": "es", "name": u"Spanish; Castilian (es)"},
    {"id": "su", "name": u"Sundanese (su)"},
    {"id": "sw", "name": u"Swahili (sw)"},
    {"id": "ss", "name": u"Swati (ss)"},
    {"id": "sv", "name": u"Swedish (sv)"},
    {"id": "ta", "name": u"Tamil (ta)"},
    {"id": "te", "name": u"Telugu (te)"},
    {"id": "tg", "name": u"Tajik (tg)"},
    {"id": "th", "name": u"Thai (th)"},
    {"id": "ti", "name": u"Tigrinya (ti)"},
    {"id": "bo", "name": u"Tibetan Standard, Tibetan, Central (bo)"},
    {"id": "tk", "name": u"Turkmen (tk)"},
    {"id": "tl", "name": u"Tagalog (tl)"},
    {"id": "tn", "name": u"Tswana (tn)"},
    {"id": "to", "name": u"Tonga (Tonga Islands) (to)"},
    {"id": "tr", "name": u"Turkish (tr)"},
    {"id": "ts", "name": u"Tsonga (ts)"},
    {"id": "tt", "name": u"Tatar (tt)"},
    {"id": "tw", "name": u"Twi (tw)"},
    {"id": "ty", "name": u"Tahitian (ty)"},
    {"id": "ug", "name": u"Uyghur, Uighur (ug)"},
    {"id": "uk", "name": u"Ukrainian (uk)"},
    {"id": "ur", "name": u"Urdu (ur)"},
    {"id": "uz", "name": u"Uzbek (uz)"},
    {"id": "ve", "name": u"Venda (ve)"},
    {"id": "vi", "name": u"Vietnamese (vi)"},
    {"id": "vo", "name": u"VolapÃ¼k (vo)"},
    {"id": "wa", "name": u"Walloon (wa)"},
    {"id": "cy", "name": u"Welsh (cy)"},
    {"id": "wo", "name": u"Wolof (wo)"},
    {"id": "fy", "name": u"Western Frisian (fy)"},
    {"id": "xh", "name": u"Xhosa (xh)"},
    {"id": "yi", "name": u"Yiddish (yi)"},
    {"id": "yo", "name": u"Yoruba (yo)"},
    {"id": "za", "name": u"Zhuang, Chuang (za)"},
    {"id": "zu", "name": u"Zulu (zu)"}
)

DISCOVER_RELEASE_TYPES = (
    {'id': 1, 'name': 32242},
    {'id': 2, 'name': 32243},
    {'id': 3, 'name': 32244},
    {'id': 4, 'name': 32245},
    {'id': 5, 'name': 32246},
    {'id': 6, 'name': 36037}
)


DISCOVER_TV_TYPES = (
    {'id': 0, 'name': 19519},
    {'id': 1, 'name': 29941},
    {'id': 2, 'name': 32221},
    {'id': 3, 'name': 32234},
    {'id': 4, 'name': 32238},
    {'id': 5, 'name': 19535},
    {'id': 6, 'name': 157},
)


DISCOVER_TV_STATUS = (
    {'id': 0, 'name': 32293},
    {'id': 1, 'name': 32294},
    {'id': 2, 'name': 32307},
    {'id': 3, 'name': 32308},
    {'id': 4, 'name': 32323},
    {'id': 5, 'name': 32324},
)


DISCOVER_WATCH_MONETIZATION_TYPES = (
    {'id': 'flatrate', 'name': 'flatrate'},
    {'id': 'free', 'name': 'free'},
    {'id': 'ads', 'name': 'ads'},
    {'id': 'rent', 'name': 'rent'},
    {'id': 'buy', 'name': 'buy'},
)

DISCOVER_SORTBY_MOVIES = (
    {'id': 'original_title.asc', 'name': 'original_title.asc'},
    {'id': 'original_title.desc', 'name': 'original_title.desc'},
    {'id': 'popularity.asc', 'name': 'popularity.asc'},
    {'id': 'popularity.desc', 'name': 'popularity.desc'},
    {'id': 'revenue.asc', 'name': 'revenue.asc'},
    {'id': 'revenue.desc', 'name': 'revenue.desc'},
    {'id': 'primary_release_date.asc', 'name': 'primary_release_date.asc'},
    {'id': 'primary_release_date.desc', 'name': 'primary_release_date.desc'},
    {'id': 'title.asc', 'name': 'title.asc'},
    {'id': 'title.desc', 'name': 'title.desc'},
    {'id': 'vote_average.asc', 'name': 'vote_average.asc'},
    {'id': 'vote_average.desc', 'name': 'vote_average.desc'},
    {'id': 'vote_count.asc', 'name': 'vote_count.asc'},
    {'id': 'vote_count.desc', 'name': 'vote_count.desc'},
)

DISCOVER_SORTBY_TV = (
    {'id': 'first_air_date.asc', 'name': 'first_air_date.asc'},
    {'id': 'first_air_date.desc', 'name': 'first_air_date.desc'},
    {'id': 'name.asc', 'name': 'name.asc'},
    {'id': 'name.desc', 'name': 'name.desc'},
    {'id': 'original_name.asc', 'name': 'original_name.asc'},
    {'id': 'original_name.desc', 'name': 'original_name.desc'},
    {'id': 'popularity.asc', 'name': 'popularity.asc'},
    {'id': 'popularity.desc', 'name': 'popularity.desc'},
    {'id': 'vote_average.asc', 'name': 'vote_average.asc'},
    {'id': 'vote_average.desc', 'name': 'vote_average.desc'},
    {'id': 'vote_count.asc', 'name': 'vote_count.asc'},
    {'id': 'vote_count.desc', 'name': 'vote_count.desc'},
)
