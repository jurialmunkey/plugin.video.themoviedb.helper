from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.window import get_property


class SyncAuthorisation:
    def __init__(self, authorisation_setting=None):
        self.authorisation_setting = authorisation_setting

    @property
    def authorisation_type(self):
        if not self.authorisation_setting:
            return 'Trakt'
        return get_setting(self.authorisation_setting, 'str')

    @property
    def is_authorized(self):
        if self.authorisation_type == 'Trakt':
            return bool(get_property('TraktIsAuth'))
        if self.authorisation_type == 'MDbList':
            return bool(get_setting('mdblist_apikey', 'str'))
        return False
