from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.files.locker import mutexlock


class SyncProviderLoadErrorDialog:
    mutex_lockname = 'SyncProviderLoadErrorDialog'

    def __init__(self, addon_id):
        self.addon_id = addon_id

    @property
    def notification_property(self):
        return f'SyncProviderLoadError.{self.addon_id}.Notified'

    @mutexlock
    def claim_notification(self):
        if get_property(self.notification_property):
            return False
        get_property(self.notification_property, 'True')
        return True

    def show(self):
        if not self.claim_notification():
            return
        from xbmcaddon import Addon
        from xbmcgui import Dialog
        name = Addon(self.addon_id).getAddonInfo('name')
        Dialog().ok(get_localized(32747), get_localized(32748).format(name))

    @mutexlock
    def clear(self):
        get_property(self.notification_property, clear_property=True)
