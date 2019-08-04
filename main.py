# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# With thanks to Roman V. M. for original simple plugin code

import sys
import xbmcgui
import xbmcplugin
import lib.utils
import lib.apis
from urllib import urlencode
from urlparse import parse_qsl
from lib.globals import _url, _handle, _addonpath, CATEGORIES, MAINFOLDER, IMAGEPATH


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

class ListItem:
    def __init__(self):
        self.name = ''  # ListItem.Label,Title
        self.dbtype = ''  # ListItem.DBType
        self.library = ''  # <content target= video, music, pictures, none>
        self.tmdb_id = ''  # ListItem.Property(tmdb_id)
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
        self.infolabels['label'] = self.name
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
            self.infolabels['imdbnumber'] = request_item['imdb_id']
        if request_item.get('runtime'):
            self.infolabels['duration'] = request_item['runtime'] * 60
        if request_item.get('tagline'):
            self.infolabels['tagline'] = request_item['tagline']
        if request_item.get('status'):
            self.infolabels['status'] = request_item['status']
        if request_item.get('genres'):
            self.infolabels['genre'] = concatinate_names(request_item.get('genres'), 'name', '/')
        if request_item.get('production_companies'):
            self.infolabels['studio'] = concatinate_names(request_item.get('production_companies'), 'name', '/')
        if request_item.get('production_countries'):
            self.infolabels['country'] = concatinate_names(request_item.get('production_countries'), 'name', '/')

    def get_properties(self, request_item):
        self.infoproperties['tmdb_id'] = self.tmdb_id
        if request_item.get('genres'):
            self.infoproperties = lib.utils.iter_props(request_item.get('genres'), 'Genre', self.infoproperties)
        if request_item.get('production_companies'):
            self.infoproperties = lib.utils.iter_props(request_item.get('production_companies'), 'Studio', self.infoproperties)
        if request_item.get('production_countries'):
            self.infoproperties = lib.utils.iter_props(request_item.get('production_countries'), 'Country', self.infoproperties)
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

    def get_dbtypes(self, tmdb_type):
        self.plural_type = lib.utils.convert_to_plural_type(tmdb_type)
        self.library = lib.utils.convert_to_library_type(tmdb_type)
        self.dbtype = lib.utils.convert_to_kodi_type(tmdb_type)
        self.infolabels['mediatype'] = self.dbtype

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
        self.next_type = ''  # &type= for next action in ListItem.FolderPath
        self.next_info = ''  # ?info= for next action in ListItem.FolderPath

    def start_container(self):
        xbmcplugin.setPluginCategory(_handle, self.name)
        container_content = self.list_type + 's' if self.list_type else ''
        xbmcplugin.setContent(_handle, container_content)

    def finish_container(self):
        xbmcplugin.endOfDirectory(_handle)

    def create_folders(self, categories, inclusions, exclusions):
        """
        Creates the folders for the plugin base folder
        """
        for key, category in categories.items():
            if key in inclusions and key not in exclusions:
                for category_type in category.get('types'):
                    listitem = ListItem()
                    listitem.plural_type = lib.utils.convert_to_plural_type(category_type)
                    listitem.name = category.get('name').format(self=listitem)
                    listitem.create_listitem(info=key, type=category_type)

    def create_listitems(self):
        for item in self.listitems:
            listitem = ListItem()
            listitem.get_title(item)
            listitem.get_poster(item)
            listitem.get_fanart(item)
            listitem.get_tmdb_id(item)
            listitem.get_info(item)
            listitem.get_properties(item)
            listitem.get_dbtypes(self.list_type)
            listitem.create_kwparams(self.next_type, self.next_info)
            listitem.create_listitem(**listitem.kwparams)

    def request_list(self):
        """
        Makes the request to TMDb API
        Can pass kwargs as additional params
        """
        if self.request_path:
            self.listitems = lib.apis.tmdb_api_request(self.request_path, **self.request_kwparams)
            if self.request_key:
                self.listitems = self.listitems[self.request_key]
        else:
            raise ValueError('No API request path specified')


class Plugin:
    def __init__(self):
        self.paramstring = sys.argv[2][1:]
        self.params = dict(parse_qsl(self.paramstring))
        self.router()

    def list_categories(self):
        """
        plugin://plugin.video.themoviedb.helper/
        The Base Dir of the plugin
        Provides all lists in MAINFOLDER
        """
        list_container = Container()
        list_container.start_container()
        list_container.create_folders(CATEGORIES, MAINFOLDER, [])
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
        list_container.list_type = lib.utils.convert_to_kodi_type(list_container.list_type)
        list_container.next_type = list_container.category.get('next_type').format(self=list_container)
        list_container.next_info = list_container.category.get('next_info').format(self=list_container)
        list_container.request_list()
        list_container.start_container()
        list_container.create_listitems()
        list_container.finish_container()


    def router(self):
        """
        Router Function
        Runs different functions depending on ?info= param
        """
        if self.params:
            if not self.params.get('info') or not self.params.get('type'):
                raise ValueError('Invalid paramstring - Must specify info and type: {0}!'.format(self.paramstring))
            elif self.params.get('info') == 'search':
                self.list_search()
            elif self.params.get('info') == 'details':
                self.list_details()
            elif self.params.get('info') in CATEGORIES:
                self.list_items()
        else:
            self.list_categories()


if __name__ == '__main__':
    Plugin()
