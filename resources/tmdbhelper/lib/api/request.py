from xbmcgui import Dialog
from tmdbhelper.lib.addon.window import get_property
from tmdbhelper.lib.addon.plugin import get_localized, get_condvisibility, get_setting
from tmdbhelper.parser import try_int
from tmdbhelper.lib.addon.tmdate import get_timestamp, set_timestamp
from tmdbhelper.lib.files.bcache import BasicCache
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.consts import CACHE_SHORT, CACHE_LONG

""" Lazyimports
from copy import copy
from json import dumps
import requests
"""


def translate_xml(request):
    """ MiniDOM alternative to ElementTree parsing of XML to dictionary """

    def dictify(r, root=True, parent_dict=None):
        if root:

            r = r.firstChild
            return {r.tagName: dictify(r, False)}

        if parent_dict is None:
            parent_dict = {}

        for c in r.childNodes:
            if c.nodeType == c.TEXT_NODE:
                parent_dict['_text'] = c.nodeValue
                continue

            child_list = parent_dict.setdefault(c.tagName, [])
            child_dict = {k: v for k, v in c.attributes.items()} if c.attributes else {}
            child_list.append(child_dict)

            if c.childNodes:
                dictify(c, False, child_dict)

        return parent_dict

    if not request:
        return

    from xml.dom.minidom import parseString
    return dictify(parseString(request.text))


def json_loads(obj):
    from json import loads
    return loads(obj)


class RequestAPI(object):
    def __init__(self, req_api_url=None, req_api_key=None, req_api_name=None, timeout=None, error_notification=get_setting('connection_notifications')):
        self.req_api_url = req_api_url or ''
        self.req_api_key = req_api_key or ''
        self.req_api_name = req_api_name or ''
        self.req_timeout_err_prop = f'TimeOutError.{self.req_api_name}'
        self.req_timeout_err = 0  # Only check last timeout on timeout since we only want to suppress when multiple
        self.req_connect_err_prop = f'ConnectionError.{self.req_api_name}'
        self.req_connect_err = get_property(self.req_connect_err_prop, is_type=float) or 0
        self.req_500_err_prop = f'500Error.{self.req_api_name}'
        self.req_500_err = get_property(self.req_500_err_prop)
        self.req_500_err = json_loads(self.req_500_err) if self.req_500_err else {}
        self.req_strip = [(self.req_api_url, self.req_api_name), (self.req_api_key, ''), ('is_xml=False', ''), ('is_xml=True', '')]
        self.headers = None
        self.timeout = timeout or 15
        self._cache = BasicCache(filename=f'{req_api_name or "requests"}.db')
        self._error_notification = error_notification
        self.translate_xml = translate_xml

    def do_error_notification(self, log_msg, note_head, note_body):
        kodi_log(log_msg, 1)
        if not self._error_notification:
            return
        Dialog().notification(note_head, note_body)

    def get_api_request_json(self, request=None, postdata=None, headers=None, is_xml=False, method=None):
        request = self.get_api_request(request=request, postdata=postdata, headers=headers, method=method)
        if not request:
            return {}
        response = self.translate_xml(request) if is_xml else request.json()
        request.close()
        return response

    def nointernet_err(self, err, log_time=900):
        # Check Kodi internet status to confirm network is down
        if get_condvisibility("System.InternetState"):
            return

        # Get the last error timestamp
        err_prop = f'NoInternetError.{self.req_api_name}'
        last_err = get_property(err_prop, is_type=float) or 0

        # Only log error and notify user if it hasn't happened in last {log_time} seconds to avoid log/gui spam
        if not get_timestamp(last_err):
            self.do_error_notification(
                f'ConnectionError: {get_localized(13297)}\n{err}\nSuppressing retries.',
                get_localized(32308).format(self.req_api_name), get_localized(13297))

        # Update our last error timestamp and return it
        return get_property(err_prop, set_timestamp(log_time))

    def connection_error(self, err, wait_time=30, msg_affix='', check_status=False):
        self.req_connect_err = set_timestamp(wait_time)
        get_property(self.req_connect_err_prop, self.req_connect_err)

        if check_status and self.nointernet_err(err):
            return

        self.do_error_notification(
            f'ConnectionError: {msg_affix} {err}\nSuppressing retries for {wait_time} seconds',
            get_localized(32308).format(' '.join([self.req_api_name, msg_affix])),
            get_localized(32307).format(f'{wait_time}'))

    def fivehundred_error(self, request, wait_time=60):
        from json import dumps
        self.req_500_err[request] = set_timestamp(wait_time)
        get_property(self.req_500_err_prop, dumps(self.req_500_err))
        self.do_error_notification(
            f'ConnectionError: {dumps(self.req_500_err)}\nSuppressing retries for {wait_time} seconds',
            get_localized(32308).format(self.req_api_name),
            get_localized(32307).format(f'{wait_time}'))

    def timeout_error(self, err):
        """ Log timeout error
        If two timeouts occur in x3 the timeout limit then set connection error
        e.g. if timeout limit is 10s then two timeouts within 30s trigger connection error
        """
        kodi_log(f'ConnectionTimeOut: {err}', 1)
        self.req_timeout_err = self.req_timeout_err or get_property(self.req_timeout_err_prop, is_type=float) or 0
        if get_timestamp(self.req_timeout_err):
            self.connection_error(err, msg_affix='timeout')
        self.req_timeout_err = set_timestamp(self.timeout * 3)
        get_property(self.req_timeout_err_prop, self.req_timeout_err)

    def get_simple_api_request(self, request=None, postdata=None, headers=None, method=None):
        import requests
        try:
            if method == 'delete':
                return requests.delete(request, headers=headers, timeout=self.timeout)
            if method == 'put':
                return requests.put(request, data=postdata, headers=headers, timeout=self.timeout)
            if method == 'json':
                return requests.post(request, json=postdata, headers=headers, timeout=self.timeout)
            if postdata or method == 'post':  # If pass postdata assume we want to post
                return requests.post(request, data=postdata, headers=headers, timeout=self.timeout)
            return requests.get(request, headers=headers, timeout=self.timeout)
        except requests.exceptions.ConnectionError as errc:
            self.connection_error(errc, check_status=True)
        except requests.exceptions.Timeout as errt:
            self.timeout_error(errt)
        except Exception as err:
            kodi_log(f'RequestError: {err}', 1)

    def get_api_request(self, request=None, postdata=None, headers=None, method=None):
        """
        Make the request to the API by passing a url request string
        """
        # Connection error in last minute for this api so don't keep trying
        if get_timestamp(self.req_connect_err):
            return
        if get_timestamp(self.req_500_err.get(request)):
            return

        # Get response
        response = self.get_simple_api_request(request, postdata, headers, method)
        if response is None or not response.status_code:
            return

        # Some error checking
        if not response.status_code == 200 and try_int(response.status_code) >= 400:  # Error Checking
            # 500 code is server error which usually indicates Trakt is down
            # In this case let's set a connection error and suppress retries for a minute
            if response.status_code == 500:
                self.fivehundred_error(request)
            # 503 code is server error which usually indicates Trakt has database maintenance
            # In this case let's set a connection error and suppress retries for five minutes
            elif response.status_code == 503:
                self.connection_error(503, wait_time=300)
            # 429 is too many requests code so suppress retries for a minute
            elif response.status_code == 429:
                self.connection_error(429)
            # Don't write 400 Bad Request error to log
            # 401 == OAuth / API key required
            elif try_int(response.status_code) > 400:
                log_level = 2 if try_int(response.status_code) in [404] else 1
                kodi_log([
                    f'HTTP Error Code: {response.status_code}',
                    f'\nRequest: {request.replace(self.req_api_key, "") if request else None}',
                    f'\nPostdata: {postdata}' if postdata else '',
                    f'\nHeaders: {headers}' if headers else '',
                    f'\nResponse: {response}' if response else ''], log_level)
            return

        # Return our response
        return response

    def get_request_url(self, *args, **kwargs):
        """
        Creates a url request string:
        https://api.themoviedb.org/3/arg1/arg2?api_key=foo&kwparamkey=kwparamvalue
        """
        url = '/'.join((self.req_api_url, '/'.join(map(str, (i for i in args if i is not None)))))
        sep = '&' if '?' in url else '?'
        if self.req_api_key:
            url = sep.join((url, self.req_api_key))
            sep = '&'
        if not kwargs:
            return url
        kws = '&'.join((f'{k}={v}' for k, v in kwargs.items() if v is not None))
        return sep.join((url, kws)) if kws else url

    def get_request_sc(self, *args, **kwargs):
        """ Get API request using the short cache """
        kwargs['cache_days'] = CACHE_SHORT
        return self.get_request(*args, **kwargs)

    def get_request_lc(self, *args, **kwargs):
        """ Get API request using the long cache """
        kwargs['cache_days'] = CACHE_LONG
        return self.get_request(*args, **kwargs)

    def get_request(
            self, *args,
            cache_days=0, cache_name='', cache_only=False, cache_force=False, cache_fallback=False, cache_refresh=False,
            cache_combine_name=False, cache_strip=[], headers=None, postdata=None, is_xml=False,
            **kwargs):
        """ Get API request from cache (or online if no cached version) """
        cache_strip = self.req_strip + cache_strip
        request_url = self.get_request_url(*args, **kwargs)
        return self._cache.use_cache(
            self.get_api_request_json, request_url,
            headers=headers or self.headers,  # Optional override to default headers.
            postdata=postdata,  # Postdata if need to POST to a RESTful API.
            is_xml=is_xml,  # Response needs translating from XML to dict
            cache_refresh=cache_refresh,  # Ignore cached timestamps and retrieve new object.
            cache_days=cache_days,  # Number of days to cache retrieved object if not already in cache.
            cache_name=cache_name,  # Affix to standard cache name.
            cache_only=cache_only,  # Only retrieve object from cache.
            cache_force=cache_force,  # Force retrieved object to be saved in cache. Use int to specify cache_days for fallback object.
            cache_fallback=cache_fallback,  # Object to force cache if no object retrieved.
            cache_combine_name=cache_combine_name,  # Combine given cache_name with auto naming via args/kwargs
            cache_strip=cache_strip)  # Strip out api key and url from cache name
