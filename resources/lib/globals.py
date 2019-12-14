LANGUAGES = [
    'ar-AE', 'ar-SA', 'be-BY', 'bg-BG', 'bn-BD', 'ca-ES', 'ch-GU', 'cs-CZ', 'da-DK', 'de-AT', 'de-CH',
    'de-DE', 'el-GR', 'en-AU', 'en-CA', 'en-GB', 'en-IE', 'en-NZ', 'en-US', 'eo-EO', 'es-ES', 'es-MX',
    'et-EE', 'eu-ES', 'fa-IR', 'fi-FI', 'fr-CA', 'fr-FR', 'gl-ES', 'he-IL', 'hi-IN', 'hu-HU', 'id-ID',
    'it-IT', 'ja-JP', 'ka-GE', 'kk-KZ', 'kn-IN', 'ko-KR', 'lt-LT', 'lv-LV', 'ml-IN', 'ms-MY', 'ms-SG',
    'nb-NO', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'si-LK', 'sk-SK', 'sl-SI',
    'sr-RS', 'sv-SE', 'ta-IN', 'te-IN', 'th-TH', 'tl-PH', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-HK',
    'zh-TW', 'zu-ZA']

TYPE_CONVERSION = {
    'movie': {
        'plural': 'Movies',
        'container': 'movies',
        'trakt': 'movie',
        'dbtype': 'movie'},
    'tv': {
        'plural': 'TV Shows',
        'container': 'tvshows',
        'trakt': 'show',
        'dbtype': 'tvshow'},
    'person': {
        'plural': 'People',
        'container': 'actors',
        'trakt': '',
        'dbtype': ''},
    'review': {
        'plural': 'Reviews',
        'container': '',
        'trakt': '',
        'dbtype': ''},
    'image': {
        'plural': 'Images',
        'container': 'images',
        'trakt': '',
        'dbtype': 'image'},
    'genre': {
        'plural': 'Genres',
        'container': 'genres',
        'trakt': '',
        'dbtype': 'genre'},
    'season': {
        'plural': 'Seasons',
        'container': 'seasons',
        'trakt': 'season',
        'dbtype': 'season'},
    'episode': {
        'plural': 'Episodes',
        'container': 'episodes',
        'trakt': 'episode',
        'dbtype': 'episode'}}

BASEDIR_MAIN = [
    {
        'info': 'dir_tmdb',
        'name': 'TheMovieDb',
        'types': [None],
        'icon': '{0}/resources/poster.png'},
    {
        'info': 'dir_trakt',
        'name': 'Trakt',
        'types': [None],
        'icon': '{0}/resources/trakt.png'}]

BASEDIR_TMDB = [
    {
        'info': 'search',
        'name': 'Search {0}',
        'types': ['movie', 'tv', 'person'],
        'icon': '{0}/resources/icons/tmdb/search.png'},
    {
        'info': 'popular',
        'name': 'Popular {0}',
        'types': ['movie', 'tv', 'person'],
        'icon': '{0}/resources/icons/tmdb/popular.png'},
    {
        'info': 'top_rated',
        'name': 'Top Rated {0}',
        'types': ['movie', 'tv'],
        'icon': '{0}/resources/icons/tmdb/toprated.png'},
    {
        'info': 'upcoming',
        'name': 'Upcoming {0}',
        'types': ['movie', 'tv'],
        'icon': '{0}/resources/icons/tmdb/upcoming.png'},
    {
        'info': 'now_playing',
        'name': 'In Theatres',
        'types': ['movie'],
        'icon': '{0}/resources/icons/tmdb/intheatres.png'},
    {
        'info': 'airing_today',
        'name': 'Airing Today',
        'types': ['tv'],
        'icon': '{0}/resources/icons/tmdb/airing.png'},
    {
        'info': 'on_the_air',
        'name': 'Currently Airing',
        'types': ['tv'],
        'icon': '{0}/resources/icons/tmdb/airing.png'},
    {
        'info': 'genres',
        'name': '{0} Genres',
        'types': ['movie', 'tv'],
        'icon': '{0}/resources/icons/tmdb/genre.png'}]

BASEDIR_TRAKT = [
    {
        'info': 'trakt_watchlist',
        'name': 'Watchlist {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_history',
        'name': 'Your Recently Watched {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_mostwatched',
        'name': 'Your Most Watched {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_inprogress',
        'name': 'Your In-Progress {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['tv']},
    {
        'info': 'trakt_recommendations',
        'name': '{0} Recommended For You',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_myairing',
        'name': 'Your {0} Airing This Week',
        'icon': '{0}/resources/trakt.png',
        'types': ['tv']},
    {
        'info': 'trakt_calendar',
        'name': 'Your {0} Calendar',
        'icon': '{0}/resources/trakt.png',
        'types': ['tv']},
    {
        'info': 'trakt_trending',
        'name': 'Trending {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_popular',
        'name': 'Popular {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_mostplayed',
        'name': 'Most Played {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_anticipated',
        'name': 'Anticipated {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie', 'tv']},
    {
        'info': 'trakt_boxoffice',
        'name': 'Top 10 Box Office {0}',
        'icon': '{0}/resources/trakt.png',
        'types': ['movie']},
    {
        'info': 'trakt_trendinglists',
        'name': 'Trending Lists',
        'icon': '{0}/resources/trakt.png',
        'types': ['both']},
    {
        'info': 'trakt_popularlists',
        'name': 'Popular Lists',
        'icon': '{0}/resources/trakt.png',
        'types': ['both']},
    {
        'info': 'trakt_likedlists',
        'name': 'Liked Lists',
        'icon': '{0}/resources/trakt.png',
        'types': ['both']},
    {
        'info': 'trakt_mylists',
        'name': 'Your Lists',
        'icon': '{0}/resources/trakt.png',
        'types': ['both']}]

BASEDIR_PATH = {'dir_tmdb': BASEDIR_TMDB, 'dir_trakt': BASEDIR_TRAKT}

DETAILED_CATEGORIES = [
    {
        'info': 'cast',
        'name': 'Cast',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'recommendations',
        'name': 'Recommended',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'similar',
        'name': 'Similar',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'crew',
        'name': 'Crew',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'posters',
        'name': 'Posters',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'fanart',
        'name': 'Fanart',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'movie_keywords',
        'name': 'Keywords',
        'icon': '',
        'types': ['movie']},
    {
        'info': 'reviews',
        'name': 'Reviews',
        'icon': '',
        'types': ['movie', 'tv']},
    {
        'info': 'stars_in_movies',
        'name': 'Cast in Movies',
        'icon': '',
        'types': ['person']},
    {
        'info': 'stars_in_tvshows',
        'name': 'Cast in TV Shows',
        'icon': '',
        'types': ['person']},
    {
        'info': 'crew_in_movies',
        'name': 'Crew in Movies',
        'icon': '',
        'types': ['person']},
    {
        'info': 'crew_in_tvshows',
        'name': 'Crew in TV Shows',
        'icon': '',
        'types': ['person']},
    {
        'info': 'images',
        'name': 'Images',
        'icon': '',
        'types': ['person']},
    {
        'info': 'seasons',
        'name': 'Seasons',
        'icon': '',
        'types': ['tv']},
    {
        'info': 'episode_cast',
        'name': 'Cast',
        'icon': '',
        'types': ['episode']},
    {
        'info': 'episode_thumbs',
        'name': 'Thumbs',
        'icon': '',
        'types': ['episode']},
    {
        'info': 'trakt_inlists',
        'name': 'In Trakt Lists',
        'icon': '',
        'url_key': 'imdb_id',
        'types': ['movie', 'tv']}]

TMDB_LISTS = {
    'search': {
        'path': 'search/{type}',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'popular': {
        'path': '{type}/popular',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'top_rated': {
        'path': '{type}/top_rated',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'upcoming': {
        'path': '{type}/upcoming',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'now_playing': {
        'path': '{type}/now_playing',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'airing_today': {
        'path': '{type}/airing_today',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'on_the_air': {
        'path': '{type}/on_the_air',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'genres': {
        'path': 'genre/{type}/list',
        'key': 'genres',
        'url_info': 'genre',
        'url_type': '{type}',
        'item_tmdbtype': 'genre'},
    'discover': {
        'path': 'discover/{type}',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'genre': {
        'path': 'discover/{type}',
        'key': 'results',
        'url_info': 'details',
        'url_ext': 'with_genres={tmdb_id}',
        'item_tmdbtype': '{type}'},
    'recommendations': {
        'path': '{type}/{tmdb_id}/recommendations',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'similar': {
        'path': '{type}/{tmdb_id}/similar',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'movie_keywords': {
        'path': '{type}/{tmdb_id}/keywords',
        'key': 'keywords',
        'url_info': 'keyword_movies',
        'item_tmdbtype': 'keyword'},
    'reviews': {
        'path': '{type}/{tmdb_id}/reviews',
        'key': 'results',
        'url_info': 'textviewer',
        'item_tmdbtype': 'review'},
    'posters': {
        'path': '{type}/{tmdb_id}/images',
        'key': 'posters',
        'url_info': 'imageviewer',
        'item_tmdbtype': 'image'},
    'fanart': {
        'path': '{type}/{tmdb_id}/images',
        'key': 'backdrops',
        'url_info': 'imageviewer',
        'item_tmdbtype': 'image'},
    'seasons': {
        'path': '{type}/{tmdb_id}',
        'key': 'seasons',
        'url_info': 'episodes',
        'url_tmdb_id': '{tmdb_id}',
        'item_tmdbtype': 'season'},
    'episode_cast': {
        'path': 'tv/{tmdb_id}/season/{season}/episode/{episode}/credits',
        'key': 'cast',
        'url_info': 'details',
        'url_tmdb_id': '{tmdb_id}',
        'item_tmdbtype': 'person'},
    'episode_thumbs': {
        'path': 'tv/{tmdb_id}/season/{season}/episode/{episode}/images',
        'key': 'stills',
        'url_info': 'imageviewer',
        'url_tmdb_id': '{tmdb_id}',
        'item_tmdbtype': 'image'},
    'stars_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'cast',
        'url_info': 'details',
        'item_tmdbtype': 'movie'},
    'stars_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'cast',
        'url_info': 'details',
        'item_tmdbtype': 'tv'},
    'crew_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'crew',
        'url_info': 'details',
        'item_tmdbtype': 'movie'},
    'crew_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'crew',
        'url_info': 'details',
        'item_tmdbtype': 'tv'},
    'images': {
        'path': 'person/{tmdb_id}/images',
        'key': 'profiles',
        'url_info': 'imageviewer',
        'item_tmdbtype': 'image'},
    'collection': {
        'path': 'collection/{tmdb_id}',
        'tmdb_check_id': 'collection',
        'key': 'parts',
        'url_info': 'details',
        'item_tmdbtype': 'movie'},
    'keyword_movies': {
        'path': 'keyword/{tmdb_id}/movies',
        'key': 'results',
        'url_info': 'details',
        'item_tmdbtype': '{type}'},
    'episodes': {
        'path': 'tv/{tmdb_id}/season/{season}',
        'key': 'episodes',
        'url_info': 'details',
        'url_tmdb_id': '{tmdb_id}',
        'item_tmdbtype': 'episode'}}

APPEND_TO_RESPONSE = 'credits,images,release_dates,content_ratings,external_ids'

TRAKT_LISTS = {
    'trakt_watchlist': {
        'path': 'users/{user_slug}/watchlist/{type}',
        'req_auth': True,
        'item_tmdbtype': '{type}'},
    'trakt_recommendations': {
        'path': 'recommendations/{type}?ignore_collected=true',
        'req_auth': True,
        'item_tmdbtype': '{type}'},
    'trakt_trending': {
        'path': '{type}/trending',
        'item_tmdbtype': '{type}'},
    'trakt_popular': {
        'path': '{type}/popular',
        'item_tmdbtype': '{type}'},
    'trakt_mostplayed': {
        'path': '{type}/played/weekly',
        'item_tmdbtype': '{type}'},
    'trakt_anticipated': {
        'path': '{type}/anticipated',
        'item_tmdbtype': '{type}'},
    'trakt_boxoffice': {
        'path': '{type}/boxoffice',
        'item_tmdbtype': '{type}'},
    'trakt_userlist': {
        'path': 'users/{user_slug}/lists/{list_slug}/items',
        'item_tmdbtype': '{type}'},
    'trakt_trendinglists': {
        'path': 'lists/trending',
        'item_tmdbtype': '{type}'},
    'trakt_popularlists': {
        'path': 'lists/popular',
        'item_tmdbtype': '{type}'},
    'trakt_likedlists': {
        'path': 'users/likes/lists',
        'req_auth': True,
        'item_tmdbtype': '{type}'},
    'trakt_mylists': {
        'path': 'users/{user_slug}/lists',
        'item_tmdbtype': '{type}'},
    'trakt_inlists': {
        'path': 'movies/{imdb_id}/lists',
        'url_key': 'imdb_id',
        'item_tmdbtype': '{type}'},
    'trakt_myairing': {
        'path': 'calendars/my/{type}',
        'req_auth': True,
        'item_tmdbtype': '{type}'},
    'trakt_airing': {
        'path': 'calendars/all/{type}',
        'item_tmdbtype': '{type}'},
    'trakt_premiering': {
        'path': 'calendars/all/{type}/premieres',
        'item_tmdbtype': '{type}'}}

TRAKT_CALENDAR = [
    ('Last Fortnight', -14, 14), ('Last Week', -7, 7), ('Yesterday', -1, 1), ('Today', 0, 1), ('Tomorrow', 1, 1),
    ('{0}', 2, 1), ('{0}', 3, 1), ('{0}', 4, 1), ('{0}', 5, 1), ('{0}', 6, 1), ('Next Week', 0, 7)]
