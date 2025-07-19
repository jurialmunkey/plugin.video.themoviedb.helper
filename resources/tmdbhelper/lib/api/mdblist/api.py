from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.api_keys.mdblist import API_KEY
from jurialmunkey.ftools import cached_property


class MDbListRatingMappingObject:
    rating_keys = {
        'tomatoes': 'rottentomatoes_rating',
        'tomatoesaudience': 'rottentomatoes_usermeter',
        'popcorn': 'rottentomatoes_usermeter'}

    rating_func = {
        'imdb': lambda v: int(v * 10),  # Convert out of /10 to 100%
        'metacriticuser': lambda v: int(v * 10),  # Convert out of /10 to 100%
        'letterboxd': lambda v: int(v * 20),  # Convert 5 stars to 100%
        'rogerebert': lambda v: int(v * 25),  # Convert 4 stars to 100%
    }

    def __init__(self, meta):
        self.meta = meta

    @cached_property
    def name(self):
        try:
            return self.meta['source']
        except KeyError:
            return

    @cached_property
    def rating_key(self):
        try:
            return self.rating_keys[self.name]
        except KeyError:
            return f'{self.name}_rating'

    @cached_property
    def rating_value(self):
        try:
            rating = None
            rating = self.meta['value']
            return self.rating_func[self.name](rating)
        except (KeyError, TypeError):  # TypeError in case of null value with integer lambda
            return rating

    @cached_property
    def votes_key(self):
        return f'{self.name}_votes'

    @cached_property
    def votes_value(self):
        try:
            return self.meta['votes']
        except KeyError:
            return

    @cached_property
    def ratings(self):
        return {
            k: v for k, v in (
                (self.rating_key, self.rating_value),
                (self.votes_key, self.votes_value)
            ) if k and v is not None
        } if self.name else {}

    def items(self):
        return self.ratings.items()


class MDbListRatingMapping:
    def __init__(self, meta):
        self.meta = meta

    @cached_property
    def meta_ratings(self):
        try:
            return self.meta['ratings']
        except (KeyError, TypeError):
            return []

    @cached_property
    def ratings(self):
        ratings = {
            k: v
            for i in self.meta_ratings
            for k, v in MDbListRatingMappingObject(i).items()
        }
        ratings['mdblist_rating'] = self.meta.get('score')
        return ratings


class MDbList(RequestAPI):

    api_key = API_KEY

    def __init__(self, api_key=None):
        api_key = api_key or self.api_key

        super(MDbList, self).__init__(
            req_api_key=f'apikey={api_key}',
            req_api_name='MDbList',
            req_api_url='https://api.mdblist.com')  # OLD API = https://mdblist.com/api
        MDbList.api_key = api_key

    def modify_static_list(self, list_id, media_type, media_id, media_provider='tmdb', action='add'):
        item = {f'{media_type}s': [{media_provider: media_id}]}
        path = self.get_request_url('lists', list_id, 'items', action)
        return self.get_api_request(path, postdata=item, method='json')

    def get_details(self, media_type, media_id, media_provider='tmdb'):
        return self.get_request_sc(media_provider, media_type, media_id)  # TODO: Add append_to_response=review ?

    def get_ratings(self, media_type, media_id, media_provider='tmdb'):
        response = self.get_details(media_type, media_id, media_provider=media_provider)
        response = MDbListRatingMapping(response)
        return response.ratings

    def get_response(self, *args, **kwargs):
        return self.get_api_request(self.get_request_url(*args, **kwargs), headers=self.headers)
