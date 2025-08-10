from xbmcgui import Dialog, DialogProgress
from jurialmunkey.parser import boolean
from jurialmunkey.window import get_property
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.trakt.token import TraktStoredAccessToken
from tmdbhelper.lib.addon.plugin import get_localized, KeyGetter
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.files.locker import mutexlock


class TraktAuthenticator:

    state = None
    progress = 0
    interval_default = 5

    def __init__(self, trakt_api):
        self.trakt_api = trakt_api

    def get_key(self, dictionary, key):
        return KeyGetter(dictionary).get_key(key)

    @property
    def attempted_login(self):
        return self.attempted_login_winprop

    @attempted_login.setter
    def attempted_login(self, value):
        self.attempted_login_winprop = get_property('TraktAttemptedLogin', f'{value}')

    @cached_property
    def attempted_login_winprop(self):
        return boolean(get_property('TraktAttemptedLogin'))

    @cached_property
    def authorization(self):
        return self.trakt_stored_access_token.authorization

    @cached_property
    def trakt_stored_access_token(self):
        return TraktStoredAccessToken(self.trakt_api)

    @property
    def access_token(self):
        return self.get_key(self.authorization, 'access_token')

    @property
    def is_authorized(self):
        return bool(self.access_token)

    def authorize(self, forced=False):
        if not self.is_authorized and forced:
            self.ask_to_login()
        return self.is_authorized

    @cached_property
    def code(self):
        return self.trakt_api.get_device_code()

    @cached_property
    def user_code(self):
        return self.get_key(self.code, 'user_code')

    @cached_property
    def device_code(self):
        return self.get_key(self.code, 'device_code')

    @cached_property
    def expires_in(self):
        return self.get_key(self.code, 'expires_in') or 0

    @cached_property
    def interval(self):
        return self.get_key(self.code, 'interval') or self.interval_default

    @cached_property
    def auth_dialog_head(self):
        return get_localized(32097)

    @cached_property
    def auth_dialog_text(self):
        return f'{get_localized(32096)}\n{get_localized(32095)}: [B]{self.user_code}[/B]'

    @cached_property
    def auth_dialog(self):
        auth_dialog = DialogProgress()
        auth_dialog.create(self.auth_dialog_head, self.auth_dialog_text)
        return auth_dialog

    @property
    def auth_dialog_route(self):
        auth_dialog_route = {
            'aborted': self.on_aborted,
            'expired': self.on_expired,
            'success': self.on_success,
        }
        return auth_dialog_route[self.state]

    @property
    def auth_dialog_progress(self):
        return int((self.progress * 100) / self.expires_in)

    def auth_dialog_update(self):
        self.progress += self.interval
        self.auth_dialog.update(self.auth_dialog_progress)

    def auth_dialog_close(self):
        self.auth_dialog.close()
        self.auth_dialog_route()

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    def on_expired(self):
        """Triggered when the device authentication code has expired"""
        kodi_log(u'Trakt authentication expired!', 1)

    def on_aborted(self):
        """Triggered when device authentication was aborted"""
        kodi_log(u'Trakt authentication aborted!', 1)

    def on_success(self):
        """Triggered when device authentication has been completed"""
        kodi_log(u'Trakt authenticated successfully!', 1)
        from tmdbhelper.lib.files.futils import json_dumps as data_dumps
        self.trakt_api.user_token.value = data_dumps(self.authorization)

    def poller(self):

        while True:

            if self.xbmc_monitor.abortRequested():
                self.state = 'aborted'
                break

            if self.auth_dialog.iscanceled():
                self.state = 'aborted'
                break

            self.auth_dialog_update()

            if self.expires_in <= self.progress:
                self.state = 'expired'
                break

            self.authorization = self.trakt_api.get_authorisation_token(self.device_code)

            if self.authorization:
                self.state = 'success'
                break

            self.xbmc_monitor.waitForAbort(self.interval)

        self.auth_dialog_close()

    mutex_lockname = 'TraktAskingForLogin'

    @mutexlock
    def ask_to_login(self):
        # We only ask once per instance to avoid spamming user with login prompts
        if self.attempted_login:
            return

        x = Dialog().yesnocustom(
            self.dialog_noapikey_header,
            self.dialog_noapikey_text,
            nolabel=get_localized(222),
            yeslabel=get_localized(186),
            customlabel=get_localized(13170)
        )
        routes = {
            1: self.login,  # Yes (OK)
            2: lambda: setattr(self, 'attempted_login', True)  # Custom (Never)
        }

        try:
            return routes[x]()
        except KeyError:
            return

    def login(self):
        if not self.user_code or not self.device_code:
            return
        self.poller()

    def logout(self, confirmation=True):
        if confirmation and not Dialog().yesno(get_localized(32212), get_localized(32213)):
            return
        return TraktStoredAccessToken(self.trakt_api).logout()
