from tmdbhelper.lib.addon.plugin import get_language
from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.api_keys.fanarttv import API_KEY, CLIENT_KEY


API_URL = 'https://webservice.fanart.tv/v3'


class FanartTV(RequestAPI):

    api_key = API_KEY
    client_key = CLIENT_KEY

    def __init__(
            self,
            api_key=None,
            client_key=None,
            language=get_language(),
            cache_only=False,
            cache_refresh=False):
        api_key = api_key or self.api_key
        client_key = client_key or self.client_key

        super(FanartTV, self).__init__(
            req_api_name='FanartTV',
            req_api_url=API_URL,
            req_api_key=f'api_key={api_key}',
            error_notification=False)
        self.req_api_key = f'api_key={api_key}' if api_key else self.req_api_key
        self.req_api_key = f'{self.req_api_key}&client_key={client_key}' if client_key else self.req_api_key
        self.language = language[:2] if language else 'en'
        self.cache_only = cache_only
        self.cache_refresh = cache_refresh
        self.req_strip.append((f'&client_key={client_key}', ''))
        FanartTV.api_key = api_key
        FanartTV.client_key = client_key
