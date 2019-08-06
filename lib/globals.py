import sys
import xbmcplugin
import xbmcaddon

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
# Get the add-on path
_addonpath = xbmcaddon.Addon().getAddonInfo('path')
# Addon name
_addonname = 'plugin.video.themoviedb.helper'
# Addon name for logging
_addonlogname = '[plugin.video.themoviedb.helper]\n'
# Get the api keys
_omdb_apikey = '?apikey=' + xbmcplugin.getSetting(_handle, 'omdb_apikey')
_tmdb_apikey = xbmcplugin.getSetting(_handle, 'tmdb_apikey')
if _tmdb_apikey:
    _waittime = 2
    _tmdb_apikey = '?api_key=' + _tmdb_apikey
else:
    _waittime = 4
    _tmdb_apikey = '?api_key=a07324c669cac4d96789197134ce272b'
# Get the language TODO: make user setting, not hardcoded
_language = '&language=en-US'
# Set http paths
OMDB_API = 'http://www.omdbapi.com/'
OMDB_ARG = '&tomatoes=True&plot=Full'
TMDB_API = 'https://api.themoviedb.org/3'
IMAGEPATH = 'https://image.tmdb.org/t/p/original/'

# Categories pass tmdb_id to path using .format(*args)
CATEGORIES = {'cast':
              {'types': ['movie', 'tv'],
               'name': 'Cast',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/credits',
               'key': 'cast',
               'list_type': '{self.request_tmdb_type}',
               'next_type': 'person',
               'next_info': 'details',
               },
              'crew':
              {'types': ['movie', 'tv'],
               'name': 'Crew',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/credits',
               'key': 'crew',
               'list_type': '{self.request_tmdb_type}',
               'next_type': 'person',
               'next_info': 'details',
               },
              'recommendations':
              {'types': ['movie', 'tv'],
               'name': 'Recommended',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/recommendations',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'similar':
              {'types': ['movie', 'tv'],
               'name': 'Similar',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/similar',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'movie_keywords':
              {'types': ['movie'],
               'name': 'Keywords',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/keywords',
               'key': 'keywords',
               'list_type': '{self.request_tmdb_type}',
               'next_type': 'keyword',
               'next_info': 'keyword_movies',
               },
              'keyword_movies':
              {'types': ['keyword'],
               'name': 'Keywords',
               'path': 'keyword/{self.request_tmdb_id}/movies',
               'key': 'results',
               'list_type': 'movie',
               'next_type': 'movie',
               'next_info': 'details',
               },
              'stars_in_movies':
              {'types': ['person'],
               'name': 'Cast in Movies',
               'path': 'person/{self.request_tmdb_id}/movie_credits',
               'key': 'cast',
               'list_type': 'movie',
               'next_type': 'movie',
               'next_info': 'details',
               },
              'stars_in_tvshows':
              {'types': ['person'],
               'name': 'Cast in Tv Shows',
               'path': 'person/{self.request_tmdb_id}/tv_credits',
               'key': 'cast',
               'list_type': 'tv',
               'next_type': 'tv',
               'next_info': 'details',
               },
              'crew_in_movies':
              {'types': ['person'],
               'name': 'Crew in Movies',
               'path': 'person/{self.request_tmdb_id}/movie_credits',
               'key': 'crew',
               'list_type': 'movie',
               'next_type': 'movie',
               'next_info': 'details',
               },
              'crew_in_tvshows':
              {'types': ['person'],
               'name': 'Crew in Tv Shows',
               'path': 'person/{self.request_tmdb_id}/tv_credits',
               'key': 'crew',
               'list_type': 'tv',
               'next_type': 'tv',
               'next_info': 'details',
               },
              'images':
              {'types': ['person'],
               'name': 'Images',
               'path': 'person/{self.request_tmdb_id}/images',
               'key': 'profiles',
               'list_type': 'image',
               'next_type': 'image',
               'next_info': 'imageviewer',
               },
              'reviews':
              {'types': ['movie', 'tv'],
               'name': 'Reviews',
               'path': '{self.request_tmdb_type}/{self.request_tmdb_id}/reviews',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '',
               'next_info': 'textviewer',
               },
              'search':
              {'types': ['movie', 'tv', 'person'],
               'name': 'Search {self.plural_type}',
               'path': 'search/{self.request_tmdb_type}',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'find':
              {'types': ['movie', 'tv'],
               'name': 'Find IMDb ID ({self.plural_type})',
               'path': 'find/{self.imdb_id}',
               'key': '{self.request_tmdb_type}_results',
               },
              'popular':
              {'types': ['movie', 'tv', 'person'],
               'name': 'Popular {self.plural_type}',
               'path': '{self.request_tmdb_type}/popular',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'top_rated':
              {'types': ['movie', 'tv'],
               'name': 'Top Rated {self.plural_type}',
               'path': '{self.request_tmdb_type}/top_rated',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'upcoming':
              {'types': ['movie'],
               'name': 'Upcoming {self.plural_type}',
               'path': '{self.request_tmdb_type}/upcoming',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'airing_today':
              {'types': ['tv'],
               'name': 'Airing Today',
               'path': '{self.request_tmdb_type}/airing_today',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'now_playing':
              {'types': ['movie'],
               'name': 'In Theatres',
               'path': '{self.request_tmdb_type}/now_playing',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'on_the_air':
              {'types': ['tv'],
               'name': 'Currently Airing',
               'path': '{self.request_tmdb_type}/on_the_air',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              'discover':
              {'types': ['movie', 'tv'],
               'name': 'Discover',
               'path': 'discover/{self.request_tmdb_type}',
               'key': 'results',
               'list_type': '{self.request_tmdb_type}',
               'next_type': '{self.request_tmdb_type}',
               'next_info': 'details',
               },
              }

MAINFOLDER = ['search', 'find', 'popular', 'top_rated', 'upcoming', 'airing_today',
              'now_playing', 'on_the_air', 'discover']

GENRE_IDS = {"Action": 28,
             "Adventure": 12,
             "Animation": 16,
             "Comedy": 35,
             "Crime": 80,
             "Documentary": 99,
             "Drama": 18,
             "Family": 10751,
             "Fantasy": 14,
             "History": 36,
             "Horror": 27,
             "Kids": 10762,
             "Music": 10402,
             "Mystery": 9648,
             "News": 10763,
             "Reality": 10764,
             "Romance": 10749,
             "Science Fiction": 878,
             "Sci-Fi & Fantasy": 10765,
             "Soap": 10766,
             "Talk": 10767,
             "TV Movie": 10770,
             "Thriller": 53,
             "War": 10752,
             "War & Politics": 10768,
             "Western": 37}
