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
from lib.globals import _url, _handle, CATEGORIES, MAINFOLDER


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


class ListItem:
    def __init__(self, item, item_tmdb_type):
        self.name = lib.utils.get_title(item)
        self.action = 'details'
        self.kodi_type = lib.utils.convert_to_kodi_type(item_tmdb_type)
        self.library_type = lib.utils.convert_to_library_type(item_tmdb_type)
        self.item_properties = {'tmdb_id': str(item.get('id', ''))}
        self.set_defaults(item, item_tmdb_type)
        self.kwactions['tmdb_id'] = self.tmdb_id

    def set_defaults(self, item, item_tmdb_type):
        self.tmdb_id = str(item.get('id', ''))
        self.item_info = {'title': self.name,
                          'mediatype': self.kodi_type}
        self.item_info = lib.utils.get_item_info(item, self.item_info)
        self.item_properties = lib.utils.get_item_properties(item, self.item_properties)
        self.art_poster = lib.utils.get_poster(item)
        self.art_fanart = lib.utils.get_fanart(item)
        self.item_art = {'thumb': self.art_poster,
                         'icon': self.art_poster,
                         'poster': self.art_poster,
                         'fanart': self.art_fanart}
        self.is_folder = True
        self.kwactions = {'info': self.action,
                          'type': item_tmdb_type}

    def create_item(self, **kwargs):
        list_item = xbmcgui.ListItem(label=self.name)
        list_item.setInfo(self.library_type, self.item_info)
        list_item.setProperties(self.item_properties)
        list_item.setArt(self.item_art)
        url = get_url(**kwargs)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, self.is_folder)


class CategoryItem(ListItem):
    def __init__(self, item, item_tmdb_type, key):
        self.plural_type = lib.utils.convert_to_plural_type(item_tmdb_type)
        self.name = item.get('name').format(self=self)
        self.tmdb_type = item_tmdb_type
        self.item_tmdb_type = item.get('item_tmdb_type').format(self=self)
        self.kodi_type = lib.utils.convert_to_kodi_type(self.item_tmdb_type)
        self.library_type = lib.utils.convert_to_library_type(self.item_tmdb_type)
        self.action = item.get('action') if item.get('action') else key
        self.item_properties = {'tmdb_id': item.get('tmdb_id')} if item.get('tmdb_id') else {}
        self.set_defaults(item, item_tmdb_type)


class Main:
    def __init__(self):
        self.paramstring = sys.argv[2][1:]
        self.params = dict(parse_qsl(self.paramstring))
        self.router()

    def generate_items(self):
        """
        Generate self.items from a TMDb list
        Passed to self.list_items()
        """
        self.tmdb_type = self.params.get('type')
        self.tmdb_id = self.params.get('tmdb_id')
        path = CATEGORIES[self.params.get('info')]['path'].format(self=self)  # Get the path from the CATEGORIES dictionary and format string
        self.request_key = CATEGORIES[self.params.get('info')]['key'].format(self=self)  # Check if we need a specific key for the request
        kwparams = lib.utils.make_kwparams(self.params)  # Strip out unneeded params before passing to TMDb API
        self.items = lib.apis.tmdb_api_request(path, **kwparams)  # Passing **kwparams allows for the skinner to pass any param to API
        self.list_items()  # Make the listitems

    def list_items(self):
        """
        List all items stored in self.items
        These items should be from a TMDb list
        """
        if self.request_key:
            self.items = self.items[self.request_key]
        self.container_content = lib.utils.convert_to_kodi_type(self.tmdb_type) + 's'
        xbmcplugin.setPluginCategory(_handle, '')  # Create directory
        xbmcplugin.setContent(_handle, self.container_content)  # Set Container.Content
        for item in self.items:
            list_item = ListItem(item, self.tmdb_type)
            list_item.create_item(**list_item.kwactions)
        xbmcplugin.endOfDirectory(_handle)  # End directory

    def list_main_categories(self):
        """
        plugin://plugin.video.themoviedb.helper/
        The Base Dir of the plugin
        Provides all lists in MAINFOLDER
        """
        xbmcplugin.setPluginCategory(_handle, '')  # Create directory
        xbmcplugin.setContent(_handle, '')  # Set Container.Content
        for key, category in CATEGORIES.items():
            if key in MAINFOLDER:
                for category_type in category.get('types'):
                    list_item = CategoryItem(category, category_type, key)
                    list_item.create_item(**list_item.kwactions)
        xbmcplugin.endOfDirectory(_handle)  # End directory

    def list_details(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=details
        Gets detailed info about tmdb_id
        Provides lists valid for tmdb_type
        """
        self.tmdb_type = self.params.get('type')
        self.tmdb_id = self.params.get('tmdb_id')
        path = '{self.tmdb_type}/{self.tmdb_id}'.format(self=self)
        kwparams = lib.utils.make_kwparams(self.params)  # Strip out unneeded params
        detailed_item = lib.apis.tmdb_api_request(path, **kwparams)  # Create the detailed item for other items to inherit
        self.container_content = lib.utils.convert_to_kodi_type(self.tmdb_type) + 's'
        xbmcplugin.setPluginCategory(_handle, '')  # Create directory
        xbmcplugin.setContent(_handle, self.container_content)  # Set Container.Content
        list_item = ListItem(detailed_item, self.tmdb_type)
        list_item.create_item(**list_item.kwactions)  # Create the main item
        for key, category in CATEGORIES.items():
            if key not in MAINFOLDER:
                for category_type in category.get('types'):
                    if category_type == self.tmdb_type:
                        category = lib.utils.merge_two_dicts(category, detailed_item)
                        list_item = CategoryItem(category, category_type, key)
                        list_item.kwactions['tmdb_id'] = self.tmdb_id
                        list_item.item_properties['tmdb_id'] = self.tmdb_id
                        list_item.item_info['mediatype'] = self.tmdb_type
                        list_item.library_type = ''
                        list_item.create_item(**list_item.kwactions)
        xbmcplugin.endOfDirectory(_handle)  # End directory

    def list_search(self):
        """
        plugin://plugin.video.themoviedb.helper/?info=search
        Search for &type= matching &query=
        Optional &year=
        """
        self.params['query'] = self.params.get('query')
        if not self.params.get('query'):
            self.params['query'] = xbmcgui.Dialog().input('Enter Search Query', type=xbmcgui.INPUT_ALPHANUM)
        if self.params.get('query'):
            self.generate_items()

    def router(self):
        """
        Router function
        Run different functions depending on ?info= param
        """
        if self.params:
            if not self.params.get('info') or not self.params.get('type'):
                raise ValueError('Invalid paramstring - Must specify info and type: {0}!'.format(self.paramstring))
            elif self.params.get('info') == 'details':
                self.list_details()
            elif self.params.get('info') == 'search':
                self.list_search()
            elif self.params.get('info') in CATEGORIES:
                self.generate_items()
        else:
            self.list_main_categories()


if __name__ == '__main__':
    Main()
