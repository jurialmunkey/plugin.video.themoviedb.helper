from tmdbhelper.lib.api.api_keys.tmdb import USER_TOKEN, API_READ_ACCESS_TOKEN
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log


API_URL = 'https://api.themoviedb.org/4'


class TMDbUserAuthenticator():

    interval = 5
    expires_in = 120
    user_token = USER_TOKEN
    api_read_access_token = API_READ_ACCESS_TOKEN

    def __init__(self, parent):
        self._parent = parent
        self.progress = 0

    @property
    def read_access_headers(self):
        return {'Authorization': f'Bearer {self.api_read_access_token}'}

    def get_request_url(self, *args, **kwargs):
        return self._parent.get_request_url(*args, **kwargs)

    def get_response_json(self, *args, **kwargs):
        return self._parent.get_response_json(*args, headers=self.read_access_headers, **kwargs)

    def get_simple_api_request(self, *args, **kwargs):
        return self._parent.get_simple_api_request(*args, headers=self.read_access_headers, **kwargs)

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    @cached_property
    def dialog_progress(self):
        from xbmcgui import DialogProgress
        return DialogProgress()

    @cached_property
    def request_token(self):
        return self.get_request_token()

    def get_request_token(self):
        request = self.create_request_token()
        if not request or not request.get('success'):
            self.dialog_ok('TMDb Get Request Token', 'Getting token from auth/request_token failed!')
            return
        return request.get('request_token')

    def create_request_token(self):
        return self.get_response_json('auth/request_token', method='post')

    @cached_property
    def request_token_url(self):
        if not self.request_token:
            return
        return f'https://www.themoviedb.org/auth/access?request_token={self.request_token}'

    @cached_property
    def request_token_qrcode(self):
        if not self.request_token_qrcode_filename:
            return
        from tmdbhelper.lib.files.futils import create_qrcode
        return create_qrcode(self.request_token_url, self.request_token_qrcode_filename)

    def delete_qrcode(self):
        if not self.request_token_qrcode_filename:
            return
        from tmdbhelper.lib.files.futils import delete_qrcode
        delete_qrcode(self.request_token_qrcode_filename)

    @cached_property
    def request_token_qrcode_filename(self):
        if not self.request_token_url:
            return
        import hashlib
        hashed = str(self.request_token).encode(errors='surrogatepass')  # Use surrogatepass to avoid emoji in filenames raising exceptions for utf-8
        return hashlib.md5(hashed).hexdigest()

    @property
    def access_token(self):
        try:
            return self._access_token
        except AttributeError:
            if not self.authorised_access:
                return
            try:
                access_token = self.authorised_access['access_token']
                self._access_token = access_token
                return self._access_token
            except KeyError:
                return

    @property
    def stored_authorisation(self):
        try:
            return self._stored_authorisation
        except AttributeError:
            from tmdbhelper.lib.files.futils import json_loads as data_loads
            try:
                token = data_loads(self.user_token.value)
            except Exception as exc:
                kodi_log(exc, 1)
                return
            if not token:
                return
            self._stored_authorisation = token
            return self._stored_authorisation

    @stored_authorisation.setter
    def stored_authorisation(self, value):
        if not value:
            return
        from tmdbhelper.lib.files.futils import json_dumps as data_dumps
        self.user_token.value = data_dumps(value)
        self._stored_authorisation = value

    def create_access_token(self):
        response = self.get_simple_api_request(self.get_request_url('auth/access_token'), postdata={'request_token': self.request_token}, method='json')
        if response is None or not response.status_code:
            return
        if response.status_code == 200:
            return response.json()
        if response.status_code == 422:
            return {'status_code': 422}

    def poller(self):
        if not self.on_poll():
            return self.on_aborted()

        if self.expires_in <= self.progress:
            return self.on_expired()

        request = self.create_access_token()

        if not request:
            return self.on_failed()

        if request.get('success') and request.get('access_token'):
            return self.on_success(request)

        self.xbmc_monitor.waitForAbort(self.interval)
        if self.xbmc_monitor.abortRequested():
            return

        return self.poller()

    def on_success(self, request):
        """Triggered when device authentication was aborted"""
        kodi_log(u'TMDb authentication success!', 1)
        self.dialog_progress_close()
        self.dialog_ok('TMDb Get Access Token', 'Successfully authenticated access token!')
        return request

    def on_failed(self):
        """Triggered when device authentication was aborted"""
        kodi_log(u'TMDb authentication failed!', 1)
        self.dialog_progress_close()

    def on_aborted(self):
        """Triggered when device authentication was aborted"""
        kodi_log(u'TMDb authentication aborted!', 1)
        self.dialog_progress_close()

    def on_expired(self):
        """Triggered when the device authentication code has expired"""
        kodi_log(u'TMDb authentication expired!', 1)
        self.dialog_progress_close()

    def on_poll(self):
        """Triggered before each poll"""
        if self.dialog_progress.iscanceled():
            return False
        self.progress += self.interval
        progress = (self.progress * 100) / self.expires_in
        self.dialog_progress.update(int(progress))
        return True

    @cached_property
    def current_window_id(self):
        from xbmcgui import getCurrentWindowDialogId
        return getCurrentWindowDialogId()

    def dialog_ok(self, header, message):
        from xbmcgui import Dialog
        Dialog().ok(header, message)

    def dialog_yesno(self, header, message):
        from xbmcgui import Dialog, DLG_YESNO_YES_BTN
        return Dialog().yesno(header, message, defaultbutton=DLG_YESNO_YES_BTN)

    def dialog_progress_create(self):
        head = 'TMDb Authorise Request Token'
        data = 'Use the displayed QR code to authenticate via another device. You must authenticate WHILE the progress dialog is open. The progress dialog will automatically close once authentication has been confirmed with the server.'
        self.dialog_progress.create(head, data)
        self.dialog_qrcode_create()

    def dialog_progress_close(self):
        self.dialog_qrcode_close()
        self.dialog_progress.close()

    @cached_property
    def dialog_qrcode_window(self):
        try:
            from xbmcgui import Window
            return Window(self.current_window_id)
        except RuntimeError:
            return

    def dialog_qrcode_create(self):
        if not self.current_window_id:
            return
        if not self.dialog_qrcode_image:
            return
        if not self.dialog_qrcode_window:
            return
        try:
            self.dialog_qrcode_window.addControl(self.dialog_qrcode_image)
        except RuntimeError:
            return

    def dialog_qrcode_close(self):
        if not self.current_window_id:
            return
        if not self.dialog_qrcode_image:
            return
        if not self.dialog_qrcode_window:
            return
        try:
            self.dialog_qrcode_window.removeControl(self.dialog_qrcode_image)
        except RuntimeError:
            return
        self.delete_qrcode()

    @cached_property
    def dialog_qrcode_image(self):
        if not self.request_token_qrcode:
            return
        try:
            from xbmcgui import ControlImage
            return ControlImage(0, 0, 324, 324, self.request_token_qrcode)
        except RuntimeError:
            return

    def revoke_login(self):
        self.user_token.value = ''

    @property
    def authorised_access(self):
        try:
            return self._authorised_access
        except AttributeError:
            authorised_access = self.get_authorised_access()
            if not authorised_access:
                return
            self._authorised_access = authorised_access
            return self._authorised_access

    def get_authorised_access(self):
        if self.stored_authorisation:
            return self.stored_authorisation

        if not self.request_token_url:
            return

        if self.dialog_yesno(
                'Open default Web Browser to Authorise?',
                'Use the default system browser to authorise TMDb Token.\nSelecting NO will display a QR code on screen that can be used to authenticate from another device.'):
            import webbrowser
            webbrowser.open(self.request_token_url, new=0, autoraise=True)

        self.dialog_progress_create()

        authorised_access = self.poller()
        if not authorised_access:
            return

        self.stored_authorisation = authorised_access
        return self.stored_authorisation
