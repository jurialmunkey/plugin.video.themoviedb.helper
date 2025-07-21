from xbmcgui import Dialog
from tmdbhelper.lib.addon.thread import SafeThread
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.addon.plugin import executebuiltin
from tmdbhelper.lib.window.constants import SV_ROUTES


class DirectCallAutoInfoDialog:
    def __init__(self, itempath, threaded=True):
        self.itempath = itempath or ''
        self.threaded = threaded

    @cached_property
    def base(self):
        try:
            return self.itempath.split('?')[0]
        except (AttributeError, IndexError):
            return

    @cached_property
    def paramstring(self):
        try:
            paramstring = self.itempath.split('?')[1]
            return paramstring.split('&&')[0]
        except (AttributeError, IndexError):
            return

    @cached_property
    def params(self):
        from jurialmunkey.parser import parse_paramstring, reconfigure_legacy_params
        return reconfigure_legacy_params(**parse_paramstring(self.paramstring))

    @property
    def listitem(self):
        return self.get_listitem()

    @busy_decorator
    def get_listitem(self):
        if not self.paramstring:
            return
        if self.base == 'plugin://plugin.video.themoviedb.helper/':
            return self.get_listitem_tmdb()
        if self.base == 'plugin://script.skinvariables/':
            return self.get_listitem_kodi()

    def get_listitem_tmdb(self):
        try:
            from tmdbhelper.lib.items.router import Router
            return Router(-1, self.paramstring).get_directory(items_only=True)[0].get_listitem()
        except (TypeError, IndexError, KeyError, AttributeError, NameError):
            return

    def get_listitem_kodi(self):
        try:
            from jurialmunkey.modimp import importmodule
            obj = importmodule(**SV_ROUTES[self.params['info']])
            obj = obj(-1, self.paramstring, **self.params)
            return obj.get_items(**self.params)[0][1]
        except (TypeError, IndexError, KeyError, AttributeError, NameError):
            return

    @staticmethod
    def force_close_info_dialogs():
        executebuiltin(f'Dialog.Close(movieinformation,true)')
        executebuiltin(f'Dialog.Close(pvrguideinfo,true)')

    def open_dialog(self):
        self.force_close_info_dialogs()
        listitem = self.listitem
        if not listitem:
            return
        Dialog().info(listitem)

    def open(self):
        if self.threaded:
            t = SafeThread(target=self.open_dialog)
            t.start()
            return t
        self.open_dialog()
