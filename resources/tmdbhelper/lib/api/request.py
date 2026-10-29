from contextvars import ContextVar
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xbmc import Monitor
import jurialmunkey.reqapi
from jurialmunkey.tmdate import get_timestamp
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.files.bcache import BasicCache


def null_function(*args, **kwargs):
    return


class RequestAPI(jurialmunkey.reqapi.RequestAPI):
    error_notification = get_setting('connection_notifications')
    _basiccache = BasicCache
    _active_request = ContextVar('tmdbhelper_api_request', default=None)

    @staticmethod
    def kodi_log(msg, level=0):
        kodi_log(msg, level)

    @staticmethod
    def get_retry_after(response):
        retry_after = response.headers.get('Retry-After', '15')
        try:
            return max(0, int(retry_after))
        except (TypeError, ValueError):
            pass
        try:
            retry_date = parsedate_to_datetime(retry_after)
            return max(0, (retry_date - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return 15

    def get_simple_api_request(self, request=None, postdata=None, headers=None, method=None):
        if get_timestamp(self.req_connect_err):
            return

        # The inherited connection retry re-enters this method; keep one 429 retry per call.
        if self._active_request.get() == (self, request):
            return super().get_simple_api_request(
                request=request, postdata=postdata, headers=headers, method=method)

        token = self._active_request.set((self, request))
        try:
            return self.get_rate_limited_request(
                request=request, postdata=postdata, headers=headers, method=method)
        finally:
            self._active_request.reset(token)

    def get_rate_limited_request(self, request=None, postdata=None, headers=None, method=None):
        response = super().get_simple_api_request(
            request=request, postdata=postdata, headers=headers, method=method)
        if response is None or response.status_code != 429:
            return response

        wait_time = self.get_retry_after(response)
        response.close()
        self.kodi_log(f'HTTP 429 from {self.req_api_name}: waiting {wait_time} seconds before retrying.', 1)
        if Monitor().waitForAbort(wait_time):
            return

        response = super().get_simple_api_request(
            request=request, postdata=postdata, headers=headers, method=method)
        if response is None or response.status_code != 429:
            return response

        wait_time = self.get_retry_after(response)
        response.close()
        self.connection_error(429, wait_time=wait_time)


class NoCacheRequestAPI(RequestAPI):
    _basiccache = null_function
