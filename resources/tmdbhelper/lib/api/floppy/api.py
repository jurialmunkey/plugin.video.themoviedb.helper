from xbmc import Monitor
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.api_keys.floppy import API_KEY
from tmdbhelper.lib.addon.consts import FLOPPY_MAX_ITEMS_PER_PAGE


class FloppyPaginatedResults:
    """ Collect every page of a limit/offset paginated Floppy endpoint """

    def __init__(self, floppy_api, *args, **kwargs):
        self.floppy_api = floppy_api
        self.args = args
        self.kwargs = kwargs
        self.monitor = Monitor()

    @cached_property
    def data(self):
        return self.get_data()

    def get_page(self, offset):
        response = self.floppy_api.get_response(*self.args, limit=FLOPPY_MAX_ITEMS_PER_PAGE, offset=offset, **self.kwargs)
        return response.json()

    def get_data(self):
        """ Returns None unless every page was retrieved so that partial data never replaces the cache """
        data = []
        offset = 0
        while not self.monitor.abortRequested():
            try:
                page = self.get_page(offset)
            except AttributeError:  # No response
                return
            data.extend(page['results'])
            if not page['pagination']['next']:
                return data
            offset += FLOPPY_MAX_ITEMS_PER_PAGE


class Floppy(RequestAPI):

    api_key = API_KEY
    json_methods = {'json_patch': 'patch'}

    def __init__(self, api_key=None, api_url=None):
        from tmdbhelper.lib.addon.plugin import get_setting
        api_key = api_key or self.api_key
        api_url = api_url or get_setting('floppy_url', 'str')

        super(Floppy, self).__init__(
            req_api_name='Floppy',
            req_api_url=f'{api_url.rstrip("/")}/api/v1')
        Floppy.api_key = api_key

        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }

    def get_request_url(self, *args, **kwargs):
        """ Floppy routes end with a trailing slash """
        return super().get_request_url(*args, '', **kwargs)

    def get_simple_api_request(self, request=None, postdata=None, headers=None, method=None):
        """ Adds JSON methods not provided by the base RequestAPI """
        try:
            session_method_name = self.json_methods[method]
        except KeyError:
            return super().get_simple_api_request(request=request, postdata=postdata, headers=headers, method=method)
        try:
            return getattr(self.session, session_method_name)(request, json=postdata, headers=headers, timeout=self.timeout)
        except self.requests.exceptions.ConnectionError as errc:
            self.connection_error(errc, check_status=True)
        except self.requests.exceptions.Timeout as errt:
            self.timeout_error(errt)

    def get_response(self, *args, **kwargs):
        return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers)

    def get_response_json(self, *args, **kwargs):
        try:
            return self.get_response(*args, **kwargs).json()
        except ValueError:
            return {}
        except AttributeError:
            return {}

    def get_paginated_results(self, *args, **kwargs):
        return FloppyPaginatedResults(self, *args, **kwargs).data

    def get_newest_value(self, *args, key='created_at', **kwargs):
        """ Value of key from the first result of a newest first query """
        try:
            return self.get_response_json(*args, limit=1, **kwargs)['results'][0][key]
        except (KeyError, IndexError):
            return

    def get_response_send(self, *args, postdata=None, method='json', **kwargs):
        return self.get_api_request(
            self.get_request_url(*args, **kwargs),
            postdata=postdata,
            headers=self.headers,
            method=method)


FLOPPY_RELOAD_PROPERTY = 'floppy.widget_reload'  # Home window property shared with plugin.video.floppy


def get_floppy_reload():
    """ Token changed by any add-on after it changes Floppy data """
    from jurialmunkey.window import get_property
    return get_property(FLOPPY_RELOAD_PROPERTY, prefix=-1)


def set_floppy_reload():
    from jurialmunkey.window import get_property
    from tmdbhelper.lib.addon.tmdate import set_timestamp
    get_property(FLOPPY_RELOAD_PROPERTY, set_property=f'{set_timestamp(0, True)}', prefix=-1)


def FloppyAPI():
    from tmdbhelper.lib.addon.plugin import get_setting
    if get_setting('floppy_apikey', 'str') and get_setting('floppy_url', 'str'):
        return Floppy()
    return
