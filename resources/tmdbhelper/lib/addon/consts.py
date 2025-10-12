CACHE_SHORT, CACHE_MEDIUM, CACHE_LONG, CACHE_EXTENDED = 1, 7, 14, 90
ITER_PROPS_MAX = 10

DAY_IN_SECONDS = 86400
DEFAULT_EXPIRY = DAY_IN_SECONDS * 30
SHORTER_EXPIRY = DAY_IN_SECONDS * 7
TEMPDAY_EXPIRY = DAY_IN_SECONDS
HALFDAY_EXPIRY = DAY_IN_SECONDS * 0.5

DATALEVEL_MIN = 1
DATALEVEL_MAX = 5
DATALEVEL_ALL = 9
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
