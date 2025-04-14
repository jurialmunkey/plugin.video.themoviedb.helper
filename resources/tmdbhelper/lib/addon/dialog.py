from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
import jurialmunkey.dialog as jurialmunkey_dialog
""" Top level module only import plugin/constants/logger """


BusyDialog = jurialmunkey_dialog.BusyDialog
busy_decorator = jurialmunkey_dialog.busy_decorator


def progress_bg(func):
    def wrapper(self, *args, **kwargs):
        self.dialog_progress_bg = DialogProgressSyncBG()
        self.dialog_progress_bg.heading = f'Updating {self.__class__.__name__}'
        self.dialog_progress_bg.create()
        data = func(self, *args, **kwargs)
        self.dialog_progress_bg.close()
        return data
    return wrapper


class DialogProgressSyncBG:
    max_value = 100
    now_value = 0
    heading = ''

    @cached_property
    def dialog_progress_bg_enabled(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return get_setting('sync_notifications')

    @cached_property
    def dialog_progress_bg(self):
        if not self.dialog_progress_bg_enabled:
            return
        from xbmcgui import DialogProgressBG
        return DialogProgressBG()

    def increment(self, x=1):
        self.now_value += x

    def update_or_create(self, progress, message, heading=None):
        if not self.dialog_progress_bg:
            return
        try:
            self.dialog_progress_bg.update(progress, message=message, heading=heading or self.heading)
        except RuntimeError:
            self.dialog_progress_bg.create(heading=heading or self.heading)
            self.dialog_progress_bg.update(progress, message=message)

    def update(self, now_value, message, heading=None):
        if not self.dialog_progress_bg:
            return
        self.now_value = now_value
        self.dialog_progress_bg.update(self.now_value, heading=heading or self.heading, message=message)

    def create(self):
        if not self.dialog_progress_bg:
            return
        self.dialog_progress_bg.create(heading=self.heading)

    def close(self):
        if not self.dialog_progress_bg:
            return
        try:
            self.dialog_progress_bg.close()
        except RuntimeError:
            pass
        del self.dialog_progress_bg

    @property
    def progress(self):
        return int((self.now_value / self.max_value) * 100)

    def set_message(self, message, heading=None):
        if not self.dialog_progress_bg:
            return
        self.update_or_create(self.progress, message=message, heading=heading)


class ProgressDialog(jurialmunkey_dialog.ProgressDialog):
    @staticmethod
    def kodi_log(msg, level=0):
        kodi_log(msg, level)
