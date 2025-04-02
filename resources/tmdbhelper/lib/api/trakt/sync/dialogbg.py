from functools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting


class DialogProgressSyncBG:
    max_value = 100
    now_value = 0
    heading = ''

    @cached_property
    def dialog_progress_bg(self):
        if not get_setting('sync_notifications'):
            return
        from xbmcgui import DialogProgressBG
        return DialogProgressBG()

    def increment(self, x=1):
        self.now_value += x

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
        self.dialog_progress_bg.close()

    @property
    def progress(self):
        return int((self.now_value / self.max_value) * 100)

    def set_message(self, message):
        if not self.dialog_progress_bg:
            return
        self.dialog_progress_bg.update(self.progress, message=message)
