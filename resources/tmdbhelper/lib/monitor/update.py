import xbmc
from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.consts import KODI_LIBRARY_LAST_UPDATED
from tmdbhelper.lib.addon.tmdate import get_timestring_zulu_now


class UpdateMonitor(xbmc.Monitor):
    """
    Monitors updating Kodi library
    """

    library_notifications = (
        'VideoLibrary.OnUpdate', 'VideoLibrary.OnRemove',
        'VideoLibrary.OnScanFinished', 'VideoLibrary.OnCleanFinished',
    )

    def __init__(self):
        super().__init__()
        self.set_library_updated()

    @staticmethod
    def set_library_updated():
        get_property(KODI_LIBRARY_LAST_UPDATED, set_property=get_timestring_zulu_now())

    def onNotification(self, sender, method, data):
        if method in self.library_notifications:
            self.set_library_updated()

    @staticmethod
    def run_library_tagger():
        from tmdbhelper.lib.addon.thread import SafeThread
        from tmdbhelper.lib.update.builder.tags import library_tagger
        SafeThread(target=library_tagger).start()

    def onScanFinished(self, library):
        if library == 'video':
            self.run_library_tagger()
