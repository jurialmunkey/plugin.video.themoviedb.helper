# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import time
import resources.lib.utils as utils
import resources.lib.apis as apis
_homewindow = xbmcgui.Window(10000)
_prefixname = 'TMDbHelper.'


class Script:
    def __init__(self):
        self.params = {}
        self.prefixpath = '{0}Path.'.format(_prefixname)
        self.prefixlock = '{0}Locked'.format(_prefixname)
        self.prefixcurrent = '{0}Current'.format(self.prefixpath)
        self.prefixposition = '{0}Position'.format(_prefixname)
        self.position = _homewindow.getProperty(self.prefixposition)
        self.position = int(self.position) if self.position else 0
        self.prevent_del = _homewindow.getProperty(self.prefixlock)
        self.prevent_del = True if self.prevent_del else False

    def get_params(self):
        for arg in sys.argv:
            if arg == 'script.py':
                pass
            elif '=' in arg:
                arg_split = arg.split('=', 1)
                if arg_split[0] and arg_split[1]:
                    key, value = arg_split
                    self.params.setdefault(key, value)
            else:
                self.params.setdefault(arg, True)

    def reset_props(self):
        _homewindow.clearProperty(self.prefixcurrent)
        _homewindow.clearProperty(self.prefixposition)
        _homewindow.clearProperty('{0}0'.format(self.prefixpath))
        _homewindow.clearProperty('{0}1'.format(self.prefixpath))

    def set_props(self, position=1, path=''):
        _homewindow.setProperty(self.prefixcurrent, path)
        _homewindow.setProperty('{0}{1}'.format(self.prefixpath, position), path)
        _homewindow.setProperty(self.prefixposition, str(position))

    def lock_path(self, condition):
        if condition:
            _homewindow.setProperty(self.prefixlock, 'True')
        else:
            self.unlock_path()

    def unlock_path(self):
        _homewindow.clearProperty(self.prefixlock)

    def call_window(self):
        sleeper = float(self.params.get('delay', '0'))
        time.sleep(sleeper)
        if self.params.get('call_id'):
            xbmc.executebuiltin('Dialog.Close(all)')
            xbmc.executebuiltin('ActivateWindow({0})'.format(self.params.get('call_id')))
        elif self.params.get('call_path'):
            xbmc.executebuiltin('Dialog.Close(all)')
            xbmc.executebuiltin('ActivateWindow(videos, {0}, return)'.format(self.params.get('call_path')))

    def router(self):
        if self.params:
            if self.params.get('add_path'):
                self.position = self.position + 1
                self.set_props(self.position, self.params.get('add_path'))
                self.lock_path(self.params.get('prevent_del'))
            elif self.params.get('add_query') and self.params.get('type'):
                tmdb_id = None
                query_list = utils.split_items(self.params.get('add_query'))
                query_index = 0
                if len(query_list) > 1:
                    query_index = xbmcgui.Dialog().select('Choose item', query_list)
                request_path = 'search/{0}'.format(self.params.get('type'))
                if query_index > -1:
                    item = apis.tmdb_api_request_longcache(request_path, query=query_list[query_index])
                else:
                    exit()
                if item and item.get('results') and isinstance(item.get('results'), list) and item.get('results')[0].get('id'):
                    item_index = 0
                    if len(item.get('results')) > 1:
                        item_list = []
                        for i in item.get('results'):
                            icon = utils.get_icon(i)
                            dialog_item = xbmcgui.ListItem(utils.get_title(i))
                            dialog_item.setArt({'icon': icon, 'thumb': icon})
                            item_list.append(dialog_item)
                        item_index = xbmcgui.Dialog().select('Choose item', item_list, preselect=0, useDetails=True)
                    if item_index > -1:
                        tmdb_id = item.get('results')[item_index].get('id')
                    else:
                        exit()
                if tmdb_id:
                    self.position = self.position + 1
                    add_paramstring = 'plugin://plugin.video.themoviedb.helper/?info=details&amp;type={0}&amp;tmdb_id={1}'.format(self.params.get('type'), tmdb_id)
                    self.set_props(self.position, add_paramstring)
                    self.lock_path(self.params.get('prevent_del'))
                else:
                    utils.kodi_log('Unable to find TMDb ID!\nQuery: {0} Type: {1}'.format(self.params.get('add_query'), self.params.get('type')), 1)
                    exit()
            elif self.params.get('del_path'):
                if self.prevent_del:
                    self.unlock_path()
                else:
                    _homewindow.clearProperty('{0}{1}'.format(self.prefixpath, self.position))
                    if self.position > 1:
                        self.position = self.position - 1
                        path = _homewindow.getProperty('{0}{1}'.format(self.prefixpath, self.position))
                        self.set_props(self.position, path)
                    else:
                        self.reset_props()
            elif self.params.get('reset_path'):
                self.reset_props()
            self.call_window()


if __name__ == '__main__':
    TMDbScript = Script()
    TMDbScript.get_params()
    TMDbScript.router()
