from xbmcgui import Dialog
from timeit import default_timer as timer
from jurialmunkey.parser import try_int
from jurialmunkey.window import get_property
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.plugin import get_localized, get_setting, ADDONPATH, KeyGetter
from tmdbhelper.lib.addon.logger import kodi_log, TimerFunc
from tmdbhelper.lib.addon.tmdate import (
    get_datetime_now,
    get_timestamp,
    get_time_difference,
    get_datetime_from_epoch,
    get_timedelta,
    set_timestamp
)


class TraktStoredAccessToken:

    refreshes_allowed = 3
    mutex_lockname = 'TraktCheckingAuthorization'
    check_auth_url = 'https://api.trakt.tv/sync/last_activities'
    access_message = ''

    def __init__(self, trakt_api):
        self.trakt_api = trakt_api

    @cached_property
    def timestamp_id(self):
        """ Get a timestamp for identifying different threads or processes """
        return get_datetime_now().strftime('%H:%M:%S.%f')

    def kodi_log(self, msg, level=1):
        kodi_log(f'[{self.timestamp_id}] {msg}', level)

    @cached_property
    def stored_authorization(self):
        return self.winprop_traktusertoken or self.get_stored_authorization()

    def get_stored_authorization(self):
        try:
            token = data_loads(self.trakt_api.user_token.value) or {}
        except Exception as exc:
            token = {}
            kodi_log(exc, 1)
        return token

    def get_key(self, key):
        return KeyGetter(self.stored_authorization).get_key(key)

    @property
    def access_token(self):
        return self.get_key('access_token')

    @property
    def refresh_token(self):
        return self.get_key('refresh_token')

    @property
    def expires_in(self):
        return self.get_key('expires_in')

    @property
    def created_at(self):
        return self.get_key('created_at')

    @property
    def created_at_datetime(self):
        if not self.created_at:
            return
        return get_datetime_from_epoch(self.created_at)

    @property
    def expires_in_timedelta(self):
        if not self.expires_in:
            return
        return get_timedelta(seconds=self.expires_in)

    @property
    def expires_in_datetime(self):
        if not self.created_at_datetime:
            return
        if not self.expires_in_timedelta:
            return
        return self.created_at_datetime + self.expires_in_timedelta

    @property
    def expires_in_timestamp(self):
        if not self.expires_in_datetime:
            return 0
        return self.expires_in_datetime.timestamp()

    @property
    def has_valid_token(self):
        if not self.expires_in_datetime:
            return False
        return bool(get_datetime_now() < self.expires_in_datetime)

    @property
    def is_expired(self):
        if not self.access_token:
            self.access_message = '[no access_token]'
            return True
        if not self.refresh_token:
            self.access_message = '[no refresh_token]'
            return True
        if not self.has_valid_token:
            self.access_message = '[present token expired]'
            return True
        if not get_timestamp(self.winprop_traktisauth):
            self.access_message = '[session token expired]'
            return True
        return False

    def confirm_authorization(self):
        response = self.trakt_api.get_simple_api_request(
            self.check_auth_url,
            headers=self.trakt_api.get_headers(self.access_token)
        )
        try:
            status_code = response.status_code
        except AttributeError:
            return False
        if status_code != 200:
            return False
        self.update_traktisauth_property()
        self.kodi_log('Trakt authentication token confirmed.')
        return True

    def authorization_check(self, refresh_token=None):
        with TimerFunc('Trakt authorization check took', inline=True) as tf:
            if refresh_token:
                self.stored_authorization = self.trakt_api.set_authorisation_token(refresh_token)
            if not self.confirm_authorization():
                return
            if get_setting('startup_notifications'):
                Dialog().notification(
                    'TMDbHelper',
                    f'Trakt authorized in {timer() - tf.timer_a:.3f}s',
                    icon=f'{ADDONPATH}/icon.png')
        return self.expires_in_timestamp

    @cached_property
    def winprop_traktisauth(self):
        winprop_traktisauth = get_property('TraktIsAuth', is_type=float)
        winprop_traktisauth = winprop_traktisauth or self.authorization_check()  # If we dont have TraktIsAuth but were asking to check it then we're on first start so lets check that the stored token is valid
        return winprop_traktisauth or 0

    @property
    def refresh_attempts(self):
        return try_int(get_property('TraktRefreshAttempts')) + 1

    def on_overrun(self):
        self.kodi_log(f'Trakt authentication exceeded limit.\n{self.access_message}')
        get_property('TraktRefreshTimeStamp', set_timestamp(300))  # Set a cooldown
        get_property('TraktRefreshAttempts', 0)  # Reset refresh attempts
        return

    def on_backoff(self):
        self.kodi_log((
            f'Trakt authentication server unavailable.\n'
            f'Next refresh attempt in {str(get_timedelta(seconds=int(get_time_difference(self.refresh_cooldown_active))))}\n'
            f'{self.access_message}'), level=2)
        return

    def on_failure(self):
        get_property('TraktRefreshAttempts', self.refresh_attempts)
        self.kodi_log(f'Trakt authentication refresh failed.\n{self.access_message}')
        return

    def on_notoken(self):
        return

    def on_current(self):
        return self.stored_authorization

    def on_success(self):
        """Triggered when device authentication has been completed"""
        self.kodi_log('Trakt authentication token refreshed.')
        self.update_stored_authorization()
        self.update_traktisauth_property()
        return self.stored_authorization

    def update_traktisauth_property(self):
        get_property('TraktIsAuth', set_property=f'{self.expires_in_timestamp}')
        get_property('TraktRefreshAttempts', 0)  # Reset refresh attempts

    def update_stored_authorization(self):
        self.trakt_api.user_token.value = self.winprop_traktusertoken = data_dumps(self.stored_authorization)

    @property
    def winprop_traktusertoken(self):
        return data_loads(get_property('TraktUserToken')) or {}

    @winprop_traktusertoken.setter
    def winprop_traktusertoken(self, value):
        return get_property('TraktUserToken', f'{value}')

    def refresh_authorization_token(self):
        return self.authorization_check(refresh_token=self.refresh_token)

    @property
    def refresh_cooldown_active(self):
        return get_timestamp(get_property('TraktRefreshTimeStamp', is_type=float) or 0)

    @mutexlock
    def get_refreshed_token(self):
        if not self.is_expired:
            return self.on_current()

        if not self.refresh_token:
            return self.on_notoken()

        if self.refresh_cooldown_active:
            return self.on_backoff()

        if self.refresh_attempts > self.refreshes_allowed:
            return self.on_overrun()

        if not self.refresh_authorization_token():
            return self.on_failure()

        return self.on_success()

    @cached_property
    def authorization(self):
        return self.get_refreshed_token()

    def logout(self):
        response = (
            self.trakt_api.del_authorisation_token(self.access_token)
            if self.access_token else None
        )
        head = get_localized(32212)
        text = (
            get_localized(32214)
            if not response else
            get_localized(32215)
            if response.status_code != 200 else
            get_localized(32216)
        )
        Dialog().ok(head, text)
