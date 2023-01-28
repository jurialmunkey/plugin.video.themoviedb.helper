from resources.lib.api.request import RequestAPI
from resources.lib.addon.consts import CACHE_SHORT, CACHE_MEDIUM
from resources.lib.api.tvdb.mapping import ItemMapper
from resources.lib.api.api_keys.tvdb import API_KEY, user_token_getter, user_token_setter


API_URL = 'https://api4.thetvdb.com/v4'


def is_authorized(func):
    def wrapper(self, *args, **kwargs):
        if not self._token:
            return
        return func(self, *args, **kwargs)
    return wrapper


class TVDb(RequestAPI):
    
    api_key = API_KEY
    get_user_token = staticmethod(user_token_getter)
    set_user_token = staticmethod(user_token_setter)
    
    def __init__(
            self,
            api_key=None,
            user_token_getter=None,
            user_token_setter=None):
        super(TVDb, self).__init__(
            req_api_name='TVDb',
            req_api_url=API_URL)
        self.mapper = ItemMapper()
        self.set_token()
        TVDb.api_key = api_key or self.api_key
        TVDb.get_user_token = staticmethod(user_token_getter or self.get_user_token)
        TVDb.set_user_token = staticmethod(user_token_setter or self.set_user_token)

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
        _token = self.get_user_token()
        if not _token:
            _token = self.login()
        return _token

    def login(self):
        path = self.get_request_url('login')
        data = self.get_api_request_json(path, postdata={'apikey': self.api_key}, method='json')
        if not data or not data.get('status') == 'success':
            return
        try:
            _token = data['data']['token']
        except (KeyError, TypeError):
            return
        self.set_user_token(_token)
        return _token

    # def get_mapped_item(self, func, *args, **kwargs):
    #     func = getattr(self, func)
    #     if not func:
    #         return
    #     data = func(*args, **kwargs)
    #     if not data:
    #         return
    #     return self.mapper.get_info(data)
