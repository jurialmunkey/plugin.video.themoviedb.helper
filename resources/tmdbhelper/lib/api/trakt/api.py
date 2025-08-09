from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.api.request import NoCacheRequestAPI
from tmdbhelper.lib.api.api_keys.trakt import CLIENT_ID, CLIENT_SECRET, USER_TOKEN
from tmdbhelper.lib.api.trakt.authenticator import TraktAuthenticator


API_URL = 'https://api.trakt.tv/'
OAUTH_DEVICE_CODE_URL = 'https://api.trakt.tv/oauth/device/code'
OAUTH_DEVICE_TOKEN_URL = 'https://api.trakt.tv/oauth/device/token'
OAUTH_REVOKE_URL = 'https://api.trakt.tv/oauth/revoke'
OAUTH_TOKEN_URL = 'https://api.trakt.tv/oauth/token'


class TraktAPI(NoCacheRequestAPI):

    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    user_token = USER_TOKEN

    def __init__(
            self,
            client_id=None,
            client_secret=None,
            user_token=None,
            login_if_required=False,
            force=False):
        super(TraktAPI, self).__init__(req_api_url=API_URL, req_api_name='TraktAPI', timeout=20)

        TraktAPI.client_id = client_id or self.client_id
        TraktAPI.client_secret = client_secret or self.client_secret
        TraktAPI.user_token = user_token or self.user_token
        self.login_if_required = login_if_required
        self.login() if force else self.authorize()

    @property
    def headers_base(self):
        return {
            'trakt-api-version': '2',
            'trakt-api-key': self.client_id,
            'Content-Type': 'application/json'
        }

    @property
    def headers(self):
        return self.get_headers(self.access_token)

    def get_headers(self, access_token=None):
        headers = {}
        headers.update(self.headers_base)
        headers.update({'Authorization': f'Bearer {access_token}'} if access_token else {})
        return headers

    @headers.setter
    def headers(self, value):
        """ Ignore base class req_api attempting to set headers """
        return

    @property
    def access_token(self):
        if not self.authenticator.access_token:
            return
        if not self.authenticator.trakt_stored_access_token.has_valid_token:
            self.refresh_authenticator()
        return self.authenticator.access_token

    @cached_property
    def authenticator(self):
        return TraktAuthenticator(self)

    def refresh_authenticator(self):
        self.authenticator = TraktAuthenticator(self)

    @cached_property
    def dialog_noapikey_header(self):
        return f'{get_localized(32007)} {self.req_api_name} {get_localized(32011)}'

    @cached_property
    def dialog_noapikey_text(self):
        return get_localized(32012)

    def get_device_code(self):
        return self.get_api_request_json(OAUTH_DEVICE_CODE_URL, postdata={
            'client_id': self.client_id
        })

    def get_authorisation_token(self, device_code):
        return self.get_api_request_json(OAUTH_DEVICE_TOKEN_URL, postdata={
            'code': device_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })

    def del_authorisation_token(self, access_token):
        return self.get_api_request(OAUTH_REVOKE_URL, postdata={
            'token': access_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })

    def set_authorisation_token(self, refresh_token):
        return self.get_api_request_json(OAUTH_TOKEN_URL, postdata={
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'grant_type': 'refresh_token'
        })

    @property
    def is_authorized(self):
        return self.authorize(forced=True)

    def authorize(self, forced=False):
        return self.authenticator.authorize(forced or self.login_if_required)

    def logout(self):
        self.refresh_authenticator()
        self.authenticator.logout()

    def login(self):
        self.refresh_authenticator()
        self.authenticator.login()

    def delete_response(self, *args, **kwargs):
        return self.get_simple_api_request(
            self.get_request_url(*args, **kwargs),
            headers=self.headers,
            method='delete')

    def post_response(self, *args, postdata=None, response_method='post', **kwargs):
        from tmdbhelper.lib.files.futils import json_dumps as data_dumps
        return self.get_simple_api_request(
            self.get_request_url(*args, **kwargs),
            headers=self.headers,
            postdata=data_dumps(postdata) if postdata else None,
            method=response_method)

    def get_response(self, *args, **kwargs):
        return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers)

    def get_response_json(self, *args, **kwargs):
        try:
            return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers).json()
        except ValueError:
            return {}
        except AttributeError:
            return {}

    @cached_property
    def trakt_syncdata(self):
        return self.get_trakt_syncdata()

    def get_trakt_syncdata(self):
        if not self.is_authorized:
            return
        from tmdbhelper.lib.api.trakt.sync.datasync import SyncData
        return SyncData(self)
