import sys
import apis
import utils
import xbmc
import xbmcgui
from urlparse import parse_qsl
from globals import GENRE_IDS, CATEGORIES, MAINFOLDER, EXCLUSIONS
from container import Container
from utils import kodi_log


class Plugin:
    def __init__(self):
        self.paramstring = sys.argv[2][1:]
        self.params = dict(parse_qsl(self.paramstring))
        self.router()

    def translate_genres(self):
        if self.params.get('with_genres'):
            self.params['with_genres'] = utils.split_items(self.params.get('with_genres'))
            temp_list = ''
            for genre in self.params.get('with_genres'):
                genre = str(GENRE_IDS.get(genre))
                if genre:
                    temp_list = '{0}%2C{1}'.format(temp_list, genre) if temp_list else genre
            if temp_list:
                self.params['with_genres'] = temp_list

    def translate_studios(self):
        if self.params.get('with_companies'):
            self.params['with_companies'] = utils.split_items(self.params.get('with_companies'))
            for studio in self.params.get('with_companies'):
                query = apis.tmdb_api_request_longcache('search/company', query=studio)
                if query and query.get('results')[0]:
                    studio_id = query.get('results')[0].get('id')
                    if studio_id:
                        temp_list = str(studio_id)
                        break  # Stop once we have a studio
            if temp_list:
                self.params['with_companies'] = temp_list

    def list_categories(self):
        """
        plugin://plugin.video.themoviedb.helper/
        The Base Dir of the plugin
        Provides all lists in MAINFOLDER
        """
        list_container = Container()
        list_container.start_container()
        list_container.create_folders(CATEGORIES, MAINFOLDER, EXCLUSIONS, '')
        list_container.finish_container()

    def list_details(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=details&type=&tmdb_id=
        Makes a request from API to get details about an item
        Lists all request lists that are compatible with item dbtype
        """
        list_container = Container()
        list_container.request_tmdb_id = self.params.get('tmdb_id')
        list_container.request_tmdb_type = self.params.get('type')
        if self.params.get('type') in ['movie', 'tv']:
            self.params['append_to_response'] = 'credits, images'
        list_container.request_path = '{self.request_tmdb_type}/{self.request_tmdb_id}'.format(self=list_container)
        list_container.request_kwparams = utils.make_kwparams(self.params)
        list_container.list_type = list_container.request_tmdb_type
        list_container.next_type = list_container.request_tmdb_type
        list_container.next_info = 'details'
        list_container.request_list()
        list_container.request_omdb_info()
        list_container.start_container()
        list_container.create_listitems()
        exclusions = MAINFOLDER
        exclusions.extend(EXCLUSIONS)
        list_container.create_folders(CATEGORIES, [], exclusions,
                                      list_container.request_tmdb_type,
                                      tmdb_id=list_container.request_tmdb_id)
        list_container.finish_container()

    def list_items(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=category&type=&tmdb_id=
        Makes a request from API and list the items
        """
        list_container = Container()
        list_container.category = CATEGORIES[self.params.get('info')]
        list_container.request_tmdb_id = self.params.get('tmdb_id')
        list_container.request_tmdb_type = self.params.get('type')
        list_container.request_filter_key = self.params.get('filter_key')
        list_container.request_filter_value = self.params.get('filter_value')
        list_container.request_path = list_container.category.get('path').format(self=list_container)
        list_container.request_key = list_container.category.get('key').format(self=list_container)
        list_container.request_kwparams = utils.make_kwparams(self.params)
        list_container.list_type = list_container.category.get('list_type').format(self=list_container)
        list_container.next_type = list_container.category.get('next_type').format(self=list_container)
        list_container.next_info = list_container.category.get('next_info').format(self=list_container)
        list_container.request_list()
        list_container.start_container()
        list_container.create_listitems()
        list_container.finish_container()

    def list_search(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=search&query=&year=
        Requests API search for item
        """
        self.params['query'] = self.params.get('query')
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.list_items()

    def list_find(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=find&type=&imdb_id=
        Find details of item based on imdb_id
        """
        self.request_tmdb_type = self.params.get('type')
        self.imdb_id = self.params.get('imdb_id')
        if not self.imdb_id and self.params.get('info') == 'find':
            self.imdb_id = xbmcgui.Dialog().input('Enter IMDb ID', type=xbmcgui.INPUT_ALPHANUM)
        if self.imdb_id:
            request_key = CATEGORIES['find']['key'].format(self=self)
            request_path = CATEGORIES['find']['path'].format(self=self)
            item = apis.tmdb_api_request_longcache(request_path, external_source='imdb_id')
            if item and item.get(request_key):
                item = item.get(request_key)[0]
                self.params['tmdb_id'] = item.get('id')
                self.params['type'] = 'movie'
                kodi_log('Found TMDb ID {0}!\n{1}'.format(self.params.get('tmdb_id'), self.paramstring), 1)
                if self.params.get('info') == 'find':
                    self.list_details()

    def check_tmdb_id(self, request_type=None):
        request_type = self.params.get('type') if not request_type else request_type
        if self.params.get('info') in MAINFOLDER:
            return
        elif self.params.get('tmdb_id'):
            return
        elif self.params.get('imdb_id'):
            self.list_find()
        elif self.params.get('query'):
            kodi_log('Searching... [No TMDb ID specified]', 0)
            request_path = 'search/{0}'.format(request_type)
            request_kwparams = utils.make_kwparams(self.params)
            item = apis.tmdb_api_request_longcache(request_path, **request_kwparams)
            if item and item.get('results') and isinstance(item.get('results'), list) and item.get('results')[0].get('id'):
                self.params['tmdb_id'] = item.get('results')[0].get('id')
                kodi_log('Found TMDb ID {0}!\n{1}'.format(self.params.get('tmdb_id'), self.paramstring), 0)
            else:
                kodi_log('Unable to find TMDb ID!\n{0}'.format(self.paramstring), 1)
        else:
            kodi_log('Must specify either &tmdb_id= &imdb_id= &query=: {0}!'.format(self.paramstring), 1)
            exit()

    def router(self):
        """
        Router Function
        Runs different functions depending on ?info= param
        """
        if self.params:
            if self.params.get('info') == 'textviewer':
                xbmcgui.Dialog().textviewer('$INFO[ListItem.Label]', '$INFO[ListItem.Plot]')
            elif self.params.get('info') == 'imageviewer':
                xbmc.executebuiltin('ShowPicture({0})'.format(self.params.get('image')))
            elif self.params.get('info') == 'discover':
                self.translate_genres()
                self.translate_studios()
                self.list_items()
            elif self.params.get('info') == 'collection':
                self.check_tmdb_id('collection')
                self.list_items()
            elif not self.params.get('info') or not self.params.get('type'):
                raise ValueError('Invalid paramstring - Must specify info and type: {0}!'.format(self.paramstring))
            elif self.params.get('info') == 'search':
                self.list_search()
            elif self.params.get('info') == 'find':
                self.list_find()
            elif self.params.get('info') == 'details':
                self.check_tmdb_id()
                self.list_details()
            elif self.params.get('info') in CATEGORIES:
                self.check_tmdb_id()
                self.list_items()
            else:
                raise ValueError('Invalid ?info= param: {0}!'.format(self.paramstring))
        else:
            self.list_categories()
