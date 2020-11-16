#!/usr/bin/env python
# -*- coding: utf-8 -*-
VALID_FILECHARS = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

ACCEPTED_MEDIATYPES = [
    'video', 'movie', 'tvshow', 'season', 'episode', 'musicvideo', 'music', 'song', 'album', 'artist']

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

IMAGEPATH_POSTER = 'https://image.tmdb.org/t/p/w500'

TMDB_GENRE_IDS = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80, "Documentary": 99, "Drama": 18,
    "Family": 10751, "Fantasy": 14, "History": 36, "Horror": 27, "Kids": 10762, "Music": 10402, "Mystery": 9648,
    "News": 10763, "Reality": 10764, "Romance": 10749, "Science Fiction": 878, "Sci-Fi & Fantasy": 10765, "Soap": 10766,
    "Talk": 10767, "TV Movie": 10770, "Thriller": 53, "War": 10752, "War & Politics": 10768, "Western": 37}

PLAYERS_URLENCODE = [
    'name', 'showname', 'clearname', 'tvshowtitle', 'title', 'thumbnail', 'poster', 'fanart',
    'originaltitle', 'plot', 'cast', 'actors']

PLAYERS_BASEDIR_USER = 'special://profile/addon_data/plugin.video.themoviedb.helper/players/'
PLAYERS_BASEDIR_SAVE = 'special://profile/addon_data/plugin.video.themoviedb.helper/reconfigured_players/'
PLAYERS_BASEDIR_BUNDLED = 'special://home/addons/plugin.video.themoviedb.helper/resources/players/'
PLAYERS_PRIORITY = 1000

NO_LABEL_FORMATTING = ['details', 'upcoming', 'trakt_calendar', 'trakt_myairing', 'trakt_anticipated', 'library_nextaired']

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
        'limit': 20
    },
    'network': {
        'type': 'tv_network',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'tv',
            'with_networks': '{tmdb_id}', 'with_id': 'True'}
    },
    'keyword': {
        'type': 'keyword',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'movie',
            'with_keywords': '{tmdb_id}', 'with_id': 'True'}
    },
    'studio': {
        'type': 'production_company',
        'sort': True,
        'limit': 2500,
        'params': {
            'info': 'discover', 'tmdb_type': 'movie',
            'with_companies': '{tmdb_id}', 'with_id': 'True'}
    }
}

RANDOMISED_LISTS = {
    'random_genres': {'info': 'genres'},
    'random_keyword': {'info': 'all_items', 'tmdb_type': 'keyword'},
    'random_trendinglists': {'info': 'trakt_trendinglists'},
    'random_popularlists': {'info': 'trakt_popularlists'},
    'random_likedlists': {'info': 'trakt_likedlists'},
    'random_mylists': {'info': 'trakt_mylists'}}

RANDOMISED_TRAKT = {
    'random_trending': 'trakt_trending',
    'random_popular': 'trakt_popular',
    'random_mostplayed': 'trakt_mostplayed',
    'random_anticipated': 'trakt_anticipated'}

TMDB_BASIC_LISTS = {
    'popular': {
        'path': '{tmdb_type}/popular',
        'key': 'results'
    },
    'top_rated': {
        'path': '{tmdb_type}/top_rated',
        'key': 'results'
    },
    'upcoming': {
        'path': '{tmdb_type}/upcoming',
        'key': 'results'
    },
    'trending_day': {
        'path': 'trending/{tmdb_type}/day',
        'key': 'results'
    },
    'trending_week': {
        'path': 'trending/{tmdb_type}/week',
        'key': 'results'
    },
    'now_playing': {
        'path': '{tmdb_type}/now_playing',
        'key': 'results'
    },
    'airing_today': {
        'path': '{tmdb_type}/airing_today',
        'key': 'results'
    },
    'on_the_air': {
        'path': '{tmdb_type}/on_the_air',
        'key': 'results'
    },
    'recommendations': {
        'path': '{tmdb_type}/{tmdb_id}/recommendations',
        'key': 'results',
        'dbid_sorting': True
    },
    'similar': {
        'path': '{tmdb_type}/{tmdb_id}/similar',
        'key': 'results',
        'dbid_sorting': True
    },
    'stars_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'cast',
        'tmdb_type': 'movie',
        'dbid_sorting': True
    },
    'stars_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'cast',
        'dbid_sorting': True,
        'tmdb_type': 'tv'
    },
    'crew_in_movies': {
        'path': 'person/{tmdb_id}/movie_credits',
        'key': 'crew',
        'dbid_sorting': True,
        'tmdb_type': 'movie'
    },
    'crew_in_tvshows': {
        'path': 'person/{tmdb_id}/tv_credits',
        'key': 'crew',
        'dbid_sorting': True,
        'tmdb_type': 'tv'
    },
    'images': {
        'path': 'person/{tmdb_id}/images',
        'key': 'profiles',
        'tmdb_type': 'image'
    },
    'videos': {
        'path': '{tmdb_type}/{tmdb_id}/videos',
        'key': 'results',
        'tmdb_type': 'video'
    },
    'posters': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'posters',
        'tmdb_type': 'image'
    },
    'fanart': {
        'path': '{tmdb_type}/{tmdb_id}/images',
        'key': 'backdrops',
        'tmdb_type': 'image'
    },
    'reviews': {
        'path': '{tmdb_type}/{tmdb_id}/reviews',
        'key': 'results'
    },
    'revenue_movies': {
        'path': 'discover/{tmdb_type}?sort_by=revenue.desc',
        'key': 'results'
    },
    'most_voted': {
        'path': 'discover/{tmdb_type}?sort_by=vote_count.desc',
        'key': 'results'
    },
    'collection': {
        'path': 'collection/{tmdb_id}',
        'key': 'parts',
        'tmdb_type': 'movie'
    },
    'movie_keywords': {
        'path': 'movie/{tmdb_id}/keywords',
        'key': 'keywords',
        'tmdb_type': 'keyword',
        'params': {
            'info': 'discover',
            'tmdb_type': 'movie',
            'with_keywords': '{tmdb_id}',
            'with_id': 'True'
        }
    },
    'genres': {
        'path': 'genre/{tmdb_type}/list',
        'key': 'genres',
        'tmdb_type': 'genre',
        'params': {
            'info': 'discover',
            'tmdb_type': '{base_tmdb_type}',
            'with_genres': '{tmdb_id}',
            'with_id': 'True'
        }
    }
}


TRAKT_BASIC_LISTS = {
    'trakt_trending': {
        'path': '{trakt_type}s/trending',
    },
    'trakt_popular': {
        'path': '{trakt_type}s/popular'
    },
    'trakt_mostplayed': {
        'path': '{trakt_type}s/played/weekly',
    },
    'trakt_anticipated': {
        'path': '{trakt_type}s/anticipated',
    },
    'trakt_boxoffice': {
        'path': '{trakt_type}s/boxoffice',
    },
    'trakt_recommendations': {
        'path': 'recommendations/{trakt_type}s?ignore_collected=true',
        'authorize': True
    },
    'trakt_myairing': {
        'path': 'calendars/my/{trakt_type}s',
        'authorize': True
    }
}


TRAKT_SYNC_LISTS = {
    'trakt_collection': {
        'sync_type': 'collection',
        'sort_by': 'title',
        'sort_how': 'asc'
    },
    'trakt_watchlist': {
        'sync_type': 'watchlist',
        'use_show_activity': True,
        'sort_by': 'unsorted'
    },
    'trakt_history': {
        'sync_type': 'watched',
        'sort_by': 'watched',
        'sort_how': 'desc'
    },
    'trakt_mostwatched': {
        'sync_type': 'watched',
        'sort_by': 'plays',
        'sort_how': 'desc'
    },
    'trakt_inprogress': {
        'sync_type': 'playback',
        'sort_by': 'paused',
        'sort_how': 'desc'
    }
}


TRAKT_LIST_OF_LISTS = {
    'trakt_trendinglists': {
        'path': 'lists/trending'},
    'trakt_popularlists': {
        'path': 'lists/popular'},
    'trakt_likedlists': {
        'path': 'users/likes/lists',
        'authorize': True},
    'trakt_mylists': {
        'path': 'users/me/lists',
        'authorize': True}
}

CONTEXT_MENU_ITEMS = {
    'tmdbhelper.context.artwork': {
        'movie': {'ftv_type': 'movie', 'ftv_id': '{ftv_id}'},
        'tvshow': {'ftv_type': 'tv', 'ftv_id': '{ftv_id}'}
    },
    'tmdbhelper.context.refresh': {
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'season': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}'},
        'other': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    },
    'tmdbhelper.context.related': {
        'episode': {'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}', 'season': '{season}', 'episode': '{episode}'},
        'other': {'tmdb_type': '{tmdb_type}', 'tmdb_id': '{tmdb_id}'}
    },
    'tmdbhelper.context.addlibrary': {
        'movie': {'info': '{tmdb_type}', 'tmdb_id': '{tmdb_id}', 'force': True},
        'tvshow': {'info': '{tmdb_type}', 'tmdb_id': '{tmdb_id}', 'force': True},
        'season': {'info': '{tmdb_type}', 'tmdb_id': '{tmdb_id}', 'force': True},
        'episode': {'info': '{tmdb_type}', 'tmdb_id': '{tmdb_id}', 'force': True}
    },
    'tmdbhelper.context.trakt': {
        'episode': {'trakt_type': '{trakt_type}', 'unique_id': '{tmdb_id}', 'id_type': 'tmdb', 'season': '{season}', 'episode': '{episode}'},
        'other': {'trakt_type': '{trakt_type}', 'unique_id': '{tmdb_id}', 'id_type': 'tmdb'}
    }
}
