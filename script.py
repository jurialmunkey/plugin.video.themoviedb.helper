# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import time
_homewindow = xbmcgui.Window(10000)
_prefixname = 'TMDbHelper.'


class Script:
    def __init__(self):
        self.params = {}
        self.prefixpath = _prefixname + 'Path.'
        self.prefixlock = _prefixname + 'Locked'
        self.prefixcurrent = self.prefixpath + 'Current'
        self.prefixposition = _prefixname + 'Position'
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
        _homewindow.clearProperty(self.prefixpath + '0')
        _homewindow.clearProperty(self.prefixpath + '1')

    def set_props(self, position=1, path=''):
        _homewindow.setProperty(self.prefixcurrent, path)
        _homewindow.setProperty(self.prefixpath + str(position), path)
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
            xbmc.executebuiltin('Dialog.Close(all, force)')
            xbmc.executebuiltin('ActivateWindow({0})'.format(self.params.get('call_id')))
        elif self.params.get('call_path'):
            xbmc.executebuiltin('Dialog.Close(all, force)')
            xbmc.executebuiltin('ActivateWindow(videos, {0}, return)'.format(self.params.get('call_path')))

    def router(self):
        if self.params:
            if self.params.get('add_path'):
                self.position = self.position + 1
                self.set_props(self.position, self.params.get('add_path'))
                self.lock_path(self.params.get('prevent_del'))
            elif self.params.get('del_path'):
                if self.prevent_del:
                    self.unlock_path()
                else:
                    _homewindow.clearProperty(self.prefixpath + str(self.position))
                    if self.position > 1:
                        self.position = self.position - 1
                        path = _homewindow.getProperty(self.prefixpath + str(self.position))
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
