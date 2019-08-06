# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# With thanks to Roman V. M. for original simple plugin code

import sys
import xbmc
import xbmcgui
import xbmcplugin
import lib.utils
from lib.utils import kodi_log
import lib.apis
from urllib import urlencode
from urlparse import parse_qsl
from lib.globals import _url, _handle, _addonpath, CATEGORIES, MAINFOLDER, IMAGEPATH, _omdb_apikey, GENRE_IDS


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


class ListItem:
    def __init__(self):
        self.name = ''  # ListItem.Label,Title
        self.dbtype = ''  # ListItem.DBType
        self.library = ''  # <content target= video, music, pictures, none>
        self.tmdb_id = ''  # ListItem.Property(tmdb_id)
        self.imdb_id = ''  # IMDb ID for item
        self.request_tmdb_type = ''  # The TMDb DBType for the Request
        self.request_tmdb_id = ''  # The TMDb ID for the Request
        self.plural_type = ''  # Plural form of category type
        self.kwparams = {}  # kwparams to contruct ListItem.FolderPath (plugin path call)
        self.poster = _addonpath + '/icon.png'  # Icon, Thumb, Poster
        self.fanart = _addonpath + '/fanart.jpg'  # Fanart
        self.is_folder = True
        self.infolabels = {}  # The item info
        self.infoproperties = {}  # The item properties
        self.infoart = {'thumb': self.poster,
                        'icon': self.poster,
                        'poster': self.poster,
                        'fanart': self.fanart}

    def get_tmdb_id(self, request_item):
        if request_item.get('id'):
            self.tmdb_id = request_item.get('id')

    def get_title(self, request_item):
        if request_item.get('title'):
            self.name = request_item.get('title')
        elif request_item.get('name'):
            self.name = request_item.get('name')
        elif request_item.get('author'):
            self.name = request_item.get('author')
        elif request_item.get('width') and request_item.get('height'):
            self.name = str(request_item['width']) + 'x' + str(request_item['height'])
        else:
            self.name = 'N/A'

    def get_fanart(self, request_item):
        if request_item.get('backdrop_path'):
            self.fanart = IMAGEPATH + request_item.get('backdrop_path')
        self.infoart['fanart'] = self.fanart

    def get_poster(self, request_item):
        if request_item.get('poster_path'):
            self.poster = IMAGEPATH + request_item.get('poster_path')
        elif request_item.get('profile_path'):
            self.poster = IMAGEPATH + request_item.get('profile_path')
        elif request_item.get('file_path'):
            self.poster = IMAGEPATH + request_item.get('file_path')
        self.infoart['poster'] = self.poster
        self.infoart['thumb'] = self.poster
        self.infoart['icon'] = self.poster

    def get_info(self, request_item):
        self.infolabels['title'] = self.name
        if request_item.get('overview'):
            self.infolabels['plot'] = request_item['overview']
        elif request_item.get('biography'):
            self.infolabels['plot'] = request_item['biography']
        elif request_item.get('content'):
            self.infolabels['plot'] = request_item['content']
        if request_item.get('vote_average'):
            self.infolabels['rating'] = request_item['vote_average']
        if request_item.get('vote_count'):
            self.infolabels['votes'] = request_item['vote_count']
        if request_item.get('release_date'):
            self.infolabels['premiered'] = request_item['release_date']
            self.infolabels['year'] = request_item['release_date'][:4]
        if request_item.get('imdb_id'):
            self.imdb_id = request_item['imdb_id']
            self.infolabels['imdbnumber'] = request_item['imdb_id']
        if request_item.get('runtime'):
            self.infolabels['duration'] = request_item['runtime'] * 60
        if request_item.get('tagline'):
            self.infolabels['tagline'] = request_item['tagline']
        if request_item.get('status'):
            self.infolabels['status'] = request_item['status']
        if request_item.get('genres'):
            self.infolabels['genre'] = lib.utils.concatinate_names(request_item.get('genres'), 'name', '/')
        if request_item.get('production_companies'):
            self.infolabels['studio'] = lib.utils.concatinate_names(request_item.get('production_companies'), 'name', '/')
        if request_item.get('production_countries'):
            self.infolabels['country'] = lib.utils.concatinate_names(request_item.get('production_countries'), 'name', '/')

    def get_properties(self, request_item):
        self.infoproperties['tmdb_id'] = self.tmdb_id
        if request_item.get('genres'):
            self.infoproperties = lib.utils.iter_props(request_item.get('genres'), 'Genre', self.infoproperties)
        if request_item.get('production_companies'):
            self.infoproperties = lib.utils.iter_props(request_item.get('production_companies'), 'Studio', self.infoproperties)
        if request_item.get('production_countries'):
            self.infoproperties = lib.utils.iter_props(request_item.get('production_countries'), 'Country', self.infoproperties)
        if request_item.get('biography'):
            self.infoproperties['biography'] = request_item['biography']
        if request_item.get('birthday'):
            self.infoproperties['birthday'] = request_item['birthday']
        if request_item.get('deathday'):
            self.infoproperties['deathday'] = request_item['deathday']
        if request_item.get('also_know_as'):
            self.infoproperties['aliases'] = request_item['also_know_as']
        if request_item.get('known_for_department'):
            self.infoproperties['role'] = request_item['known_for_department']
        if request_item.get('place_of_birth'):
            self.infoproperties['born'] = request_item['place_of_birth']
        if request_item.get('budget'):
            self.infoproperties['budget'] = '${:0,.0f}'.format(request_item['budget'])
        if request_item.get('revenue'):
            self.infoproperties['revenue'] = '${:0,.0f}'.format(request_item['revenue'])

    def get_omdb_info(self, request_item):
        if request_item.get('rated'):
            self.infolabels['MPAA'] = 'Rated ' + request_item.get('rated')
        if request_item.get('awards'):
            self.infoproperties['awards'] = request_item.get('awards')
        if request_item.get('metascore'):
            self.infoproperties['metacritic_rating'] = request_item.get('metascore')
        if request_item.get('imdbRating'):
            self.infoproperties['imdb_rating'] = request_item.get('imdbRating')
        if request_item.get('imdbVotes'):
            self.infoproperties['imdb_votes'] = request_item.get('imdbVotes')
        if request_item.get('tomatoMeter'):
            self.infoproperties['rottentomatoes_rating'] = request_item.get('tomatoMeter')
        if request_item.get('tomatoImage'):
            self.infoproperties['rottentomatoes_image'] = request_item.get('tomatoImage')
        if request_item.get('tomatoReviews'):
            self.infoproperties['rottentomatoes_reviewtotal'] = request_item.get('tomatoReviews')
        if request_item.get('tomatoFresh'):
            self.infoproperties['rottentomatoes_reviewsfresh'] = request_item.get('tomatoFresh')
        if request_item.get('tomatoRotten'):
            self.infoproperties['rottentomatoes_reviewsrotten'] = request_item.get('tomatoRotten')
        if request_item.get('tomatoConsensus'):
            self.infoproperties['rottentomatoes_consensus'] = request_item.get('tomatoConsensus')
        if request_item.get('tomatoUserMeter'):
            self.infoproperties['rottentomatoes_usermeter'] = request_item.get('tomatoUserMeter')
        if request_item.get('tomatoUserReviews'):
            self.infoproperties['rottentomatoes_userreviews'] = request_item.get('tomatoUserReviews')

    def get_autofilled_info(self, item):
        self.get_poster(item)
        self.get_fanart(item)
        self.get_tmdb_id(item)
        self.get_info(item)
        self.get_properties(item)

    def get_dbtypes(self, tmdb_type):
        self.plural_type = lib.utils.convert_to_plural_type(tmdb_type)
        self.library = lib.utils.convert_to_library_type(tmdb_type)
        self.dbtype = lib.utils.convert_to_kodi_type(tmdb_type)
        self.infolabels['mediatype'] = self.dbtype
        self.infoproperties['tmdb_type'] = tmdb_type

    def create_kwparams(self, next_type, next_info, **kwargs):
        self.kwparams['type'] = next_type
        self.kwparams['info'] = next_info
        self.kwparams['tmdb_id'] = self.tmdb_id
        for key, value in kwargs.items():
            if value:
                self.kwparams[key] = value

    def create_listitem(self, **kwargs):
        self.listitem = xbmcgui.ListItem(label=self.name)
        self.listitem.setInfo(self.library, self.infolabels)
        self.listitem.setProperties(self.infoproperties)
        self.listitem.setArt(self.infoart)
        if kwargs.get('info') == 'textviewer':
            self.url = get_url(info='textviewer')
        elif kwargs.get('info') == 'imageviewer':
            self.url = get_url(info='imageviewer', image=self.poster)
        else:
            self.url = get_url(**kwargs)
        xbmcplugin.addDirectoryItem(_handle, self.url, self.listitem, self.is_folder)


class Container:
    def __init__(self):
        self.name = ''  # Container.PluginCategory
        self.list_type = ''  # DBType of Items in List
        self.request_tmdb_id = ''  # TMDb ID to request
        self.request_tmdb_type = ''  # TMDb ID to request
        self.request_path = ''  # TMDb path to request
        self.request_key = ''  # The JSON key containing our request
        self.request_kwparams = {}  # Additional kwparams to pass to request
        self.omdb_info = {}  # OMDb info dict
        self.next_type = ''  # &type= for next action in ListItem.FolderPath
        self.next_info = ''  # ?info= for next action in ListItem.FolderPath
        self.listitems = []  # The list of items to add

    def start_container(self):
        xbmcplugin.setPluginCategory(_handle, self.name)
        container_content = lib.utils.convert_to_kodi_type(self.list_type) + 's' if self.list_type else ''
        xbmcplugin.setContent(_handle, container_content)

    def finish_container(self):
        xbmcplugin.endOfDirectory(_handle)

    def create_folders(self, categories, inclusions, exclusions, dbtype, **kwargs):
        """
        Creates the folders for plugin base and ?info=details
        Includes keys matching inclusions and excludes key matching exclusions
        Constructs a folder for each type (or the specified dbtype) per each permitted key
        """
        for key, category in sorted(categories.items(), key=lambda keycat: keycat[1].get('index')):
            if not inclusions or key in inclusions:
                if not exclusions or key not in exclusions:
                    for category_type in category.get('types'):
                        if not dbtype or category_type == dbtype:
                            listitem = ListItem()
                            listitem.request_tmdb_type = category_type
                            listitem.plural_type = lib.utils.convert_to_plural_type(category_type)
                            listitem.name = category.get('name').format(self=listitem)
                            if category.get('list_type'):
                                category_type = category.get('list_type').format(self=listitem)
                            if self.listitems:
                                listitem.get_autofilled_info(self.listitems[0])
                                listitem.get_dbtypes(self.list_type)
                            if self.omdb_info:
                                listitem.get_omdb_info(self.omdb_info)
                            listitem.create_listitem(info=key, type=category_type, **kwargs)

    def create_listitems(self):
        for item in self.listitems:
            listitem = ListItem()
            listitem.get_title(item)
            listitem.get_autofilled_info(item)
            listitem.get_dbtypes(self.list_type)
            if self.omdb_info:
                listitem.get_omdb_info(self.omdb_info)
            listitem.create_kwparams(self.next_type, self.next_info)
            listitem.create_listitem(**listitem.kwparams)

    def request_omdb_info(self):
        if self.request_tmdb_type in ['movie', 'tv']:
            if _omdb_apikey and self.listitems:
                if self.listitems[0].get('imdb_id'):
                    self.imdb_id = self.listitems[0].get('imdb_id')
                    self.omdb_info = lib.apis.omdb_api_request(i=self.imdb_id)

    def request_list(self):
        """
        Makes the request to TMDb API
        Can pass kwargs as additional params
        Checks if a certain request_key is needed and provides that key
        Converts a single item dict to a list containing the dict for iteration purposes
        """
        if self.request_path:
            self.listitems = lib.apis.tmdb_api_request(self.request_path, **self.request_kwparams)
            if self.request_key:
                self.listitems = self.listitems[self.request_key]
            if self.listitems and not isinstance(self.listitems, list):
                self.listitems = [self.listitems]
        else:
            raise ValueError('No API request path specified')


class Plugin:
    def __init__(self):
        self.paramstring = sys.argv[2][1:]
        self.params = dict(parse_qsl(self.paramstring))
        self.router()

    def translate_genres(self):
        if self.params.get('with_genres'):
            if ' / ' in self.params.get('with_genres'):
                self.params['with_genres'] = self.params.get('with_genres').split(' / ')
            temp_list = ''
            for genre in self.params.get('with_genres'):
                genre = str(GENRE_IDS.get(genre))
                if genre:
                    temp_list = temp_list + '%2C' + genre if temp_list else genre
            if temp_list:
                self.params['with_genres'] = temp_list

    def translate_studios(self):
        if self.params.get('with_companies'):
            if ' / ' in self.params.get('with_companies'):
                self.params['with_companies'] = self.params.get('with_companies').split(' / ')
            temp_list = ''
            for studio in self.params.get('with_companies'):
                query = lib.apis.tmdb_api_request_longcache('search/company', query=studio)
                if query and query.get('results')[0]:
                    studio = str(query.get('results')[0].get('id'))
                    if studio:
                        temp_list = studio
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
        list_container.create_folders(CATEGORIES, MAINFOLDER, ['discover'], '')
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
        list_container.request_path = '{self.request_tmdb_type}/{self.request_tmdb_id}'.format(self=list_container)
        list_container.request_kwparams = lib.utils.make_kwparams(self.params)
        list_container.list_type = list_container.request_tmdb_type
        list_container.next_type = list_container.request_tmdb_type
        list_container.next_info = 'details'
        list_container.request_list()
        list_container.request_omdb_info()
        list_container.start_container()
        list_container.create_listitems()
        list_container.create_folders(CATEGORIES, [], MAINFOLDER,
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
        list_container.request_path = list_container.category.get('path').format(self=list_container)
        list_container.request_key = list_container.category.get('key').format(self=list_container)
        list_container.request_kwparams = lib.utils.make_kwparams(self.params)
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
            item = lib.apis.tmdb_api_request_longcache(request_path, external_source='imdb_id')
            if item and item.get(request_key):
                item = item.get(request_key)[0]
                self.params['tmdb_id'] = item.get('id')
                self.params['type'] = 'movie'
                kodi_log('Found TMDb ID {0}!\n{1}'.format(self.params.get('tmdb_id'), self.paramstring), 1)
                if self.params.get('info') == 'find':
                    self.list_details()

    def check_tmdb_id(self):
        if self.params.get('info') in MAINFOLDER:
            return
        elif self.params.get('tmdb_id'):
            return
        elif self.params.get('imdb_id'):
            self.list_find()
        elif self.params.get('query'):
            kodi_log('Searching... [No TMDb ID specified]', 0)
            request_path = 'search/' + self.params.get('type')
            request_kwparams = lib.utils.make_kwparams(self.params)
            item = lib.apis.tmdb_api_request_longcache(request_path, **request_kwparams)
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
                xbmc.executebuiltin('ShowPicture(' + self.params.get('image') + ')')
            elif self.params.get('info') == 'discover':
                self.translate_genres()
                self.translate_studios()
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


if __name__ == '__main__':
    Plugin()
