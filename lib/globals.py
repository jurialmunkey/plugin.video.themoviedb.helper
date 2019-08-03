import sys
import xbmcplugin
import xbmcaddon

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
# Get the add-on path
_addonpath = xbmcaddon.Addon().getAddonInfo('path')
# Get the api keys
_omdb_apikey = xbmcplugin.getSetting(_handle, 'omdb_apikey')
_tmdb_apikey = '?api_key=' + xbmcplugin.getSetting(_handle, 'tmdb_apikey')
# Get the language TODO: make user setting, not hardcoded
_language = '&language=en-US'
# Set http paths
OMDB_API = 'http://www.omdbapi.com/'
TMDB_API = 'https://api.themoviedb.org/3'
IMAGEPATH = 'https://image.tmdb.org/t/p/original/'

# Categories pass tmdb_id to path using .format(*args)
CATEGORIES = {'cast':
              {'types': ['movie', 'tv'],
               'name': 'Cast',
               'path': '{self.tmdb_type}/{self.tmdb_id}/credits',
               'key': 'cast',
               'item_tmdb_type': 'person',
               },
              'crew':
              {'types': ['movie', 'tv'],
               'name': 'Crew',
               'path': '{self.tmdb_type}/{self.tmdb_id}/credits',
               'key': 'crew',
               'item_tmdb_type': 'person',
               },
              'recommendations':
              {'types': ['movie', 'tv'],
               'name': 'Recommended',
               'path': '{self.tmdb_type}/{self.tmdb_id}/recommendations',
               'key': 'results',
               'item_tmdb_type': '{self.tmdb_type}',
               },
              'similar':
              {'types': ['movie', 'tv'],
               'name': 'Similar',
               'path': '{self.tmdb_type}/{self.tmdb_id}/similar',
               'key': 'results',
               'item_tmdb_type': '{self.tmdb_type}',
               },
              'keywords_movie':
              {'types': ['movie'],
               'name': 'Keywords',
               'path': '{self.tmdb_type}/{self.tmdb_id}/keywords',
               'key': 'keywords',
               'item_tmdb_type': '',
               },
              'keywords_tv':
              {'types': ['tv'],
               'name': 'Keywords',
               'path': '{self.tmdb_type}/{self.tmdb_id}/keywords',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'search':
              {'types': ['movie', 'tv', 'person'],
               'name': 'Search {self.plural_type}',
               'path': 'search/{self.tmdb_type}',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'find':
              {'types': ['movie', 'tv'],
               'name': 'Find IMDb ID ({self.plural_type})',
               'path': 'find/{self.imdb_id}',
               'key': '{self.tmdb_type}_results',
               'item_tmdb_type': '',
               'action': 'details',
               },
              'popular':
              {'types': ['movie', 'tv', 'person'],
               'name': 'Popular {self.plural_type}',
               'path': '{self.tmdb_type}/popular',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'top_rated':
              {'types': ['movie', 'tv'],
               'name': 'Top Rated {self.plural_type}',
               'path': '{self.tmdb_type}/top_rated',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'upcoming':
              {'types': ['movie'],
               'name': 'Upcoming {self.plural_type}',
               'path': '{self.tmdb_type}/upcoming',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'airing_today':
              {'types': ['tv'],
               'name': 'Airing Today',
               'path': '{self.tmdb_type}/airing_today',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'now_playing':
              {'types': ['movie'],
               'name': 'In Theatres',
               'path': '{self.tmdb_type}/now_playing',
               'key': 'results',
               'item_tmdb_type': '',
               },
              'on_the_air':
              {'types': ['tv'],
               'name': 'Currently Airing',
               'path': '{self.tmdb_type}/on_the_air',
               'key': 'results',
               'item_tmdb_type': '',
               },
              }

MAINFOLDER = ['search', 'find', 'popular', 'top_rated',
              'upcoming', 'airing_today', 'now_playing',
              'on_the_air']
