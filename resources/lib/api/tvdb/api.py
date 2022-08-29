from resources.lib.api.request import RequestAPI
from resources.lib.addon.plugin import get_setting, set_setting
from resources.lib.addon.consts import CACHE_SHORT, CACHE_MEDIUM
from resources.lib.api.tvdb.mapping import ItemMapper
from tmdbhelper.parser import load_in_data


API_URL = 'https://api4.thetvdb.com/v4'


def is_authorized(func):
    def wrapper(self, *args, **kwargs):
        if not self._token:
            return
        return func(self, *args, **kwargs)
    return wrapper


class TVDb(RequestAPI):
    def __init__(self):
        super(TVDb, self).__init__(
            req_api_name='TVDb',
            req_api_url=API_URL)
        self.mapper = ItemMapper()
        self.set_token()

    def set_token(self):
        self._token = self.get_token()
        self.headers = {'Authorization': f'Bearer {self._token}'}

    @is_authorized
    def get_request_sc(self, *args, **kwargs):
        """ Get API request using the short cache """
        kwargs['cache_days'] = CACHE_SHORT
        data = self.get_request(*args, **kwargs)
        try:
            data = data['data']
        except (KeyError, AttributeError, TypeError):
            return
        return data

    @is_authorized
    def get_request_lc(self, *args, **kwargs):
        """ Get API request using the long cache """
        kwargs['cache_days'] = CACHE_MEDIUM
        data = self.get_request(*args, **kwargs)
        try:
            data = data['data']
        except (KeyError, AttributeError, TypeError):
            return
        return data

    @is_authorized
    def get_response_json(self, *args, **kwargs):
        return self.get_api_request_json(self.get_request_url(*args, **kwargs), headers=self.headers)

    def get_token(self):
        _token = get_setting('tvdb_token', 'str')
        if not _token:
            _token = self.login()
        return _token

    def login(self):
        path = self.get_request_url('login')
        data = self.get_api_request_json(path, postdata={
            'apikey': load_in_data(
                b"#SFK\x03JI\x06N\x11\x04GY\x03\x14'\x0c_Y\x19\x0f]\x0c]\x00\x13\x01^JP\x11g(|\x03*",
                b'Be respectful. Dont jeopardise TMDbHelper access to this data by stealing API keys or changing item limits.').decode()},
            method='json')
        if not data or not data.get('status') == 'success':
            return
        try:
            _token = data['data']['token']
        except (KeyError, TypeError):
            return
        set_setting('tvdb_token', _token, 'str')
        return _token

    # def get_mapped_item(self, func, *args, **kwargs):
    #     func = getattr(self, func)
    #     if not func:
    #         return
    #     data = func(*args, **kwargs)
    #     if not data:
    #         return
    #     return self.mapper.get_info(data)
