from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.api.contains import CommonContainerAPIs


DEFAULT_API = object()


class SyncAuthorisation(CommonContainerAPIs):
    def __init__(self, authorisation_setting=None, trakt_api=DEFAULT_API, mdblist_api=DEFAULT_API):
        self.authorisation_setting = authorisation_setting
        if trakt_api is not DEFAULT_API:
            self.trakt_api = trakt_api
        if mdblist_api is not DEFAULT_API:
            self.mdblist_api = mdblist_api

    @property
    def authorisation_type(self):
        if not self.authorisation_setting:
            return 'Trakt'
        return get_setting(self.authorisation_setting, 'str')

    @property
    def is_authorized(self):
        if self.authorisation_type == 'Trakt':
            return self.trakt_api.authenticator.is_authorized
        if self.authorisation_type == 'MDbList':
            return self.mdblist_api is not None
        return False
