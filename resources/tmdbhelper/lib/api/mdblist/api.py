from tmdbhelper.lib.api.request import RequestAPI
from tmdbhelper.lib.api.api_keys.mdblist import API_KEY
from tmdbhelper.lib.addon.plugin import ADDONPATH
from tmdbhelper.lib.items.itemlist import ItemListPagination, ListPagination


class MDbListPaginationLists(ListPagination):
    """ Paginates and configures items in a list of lists """

    @staticmethod
    def map_item(i):
        item = {}
        item['label'] = i.get('name')
        item['infolabels'] = {'plot': i.get('description'), 'studio': [i.get('user_name')]}
        item['art'] = {'icon': f'{ADDONPATH}/resources/icons/mdblist/mdblist.png'}
        item['params'] = {
            'info': 'mdblist_userlist',
            'list_name': i.get('name'),
            'list_id': i.get('id'),
            'plugin_category': i.get('name')}
        item['unique_ids'] = {
            'mdblist': i.get('id'),
            'slug': i.get('slug'),
            'user': i.get('user_id')}
        if i.get('dynamic'):
            item['params']['dynamic'] = 'true'
        return item

    @property
    def items(self):
        try:
            return self._items
        except AttributeError:
            self.update_pagination()
            return self._items

    def update_pagination(self):
        self._paginated_items = self.get_updated_pagination()
        self._items = [j for j in (self.map_item(i) for i in self.paginated_items.items) if j]


class MDbListRatingMapping():
    ratings_translation = {
        'tomatoes': 'rottentomatoes_rating',
        'tomatoesaudience': 'rottentomatoes_usermeter',
        'popcorn': 'rottentomatoes_usermeter'}

    def __init__(self, meta):
        self.meta = meta

    @property
    def meta_ratings(self):
        try:
            return self.meta['ratings']
        except (KeyError, TypeError):
            return []

    @property
    def ratings(self):
        try:
            return self._ratings
        except AttributeError:
            return self.get_ratings()

    def get_ratings(self):
        ratings = {}
        ratings['mdblist_rating'] = self.meta.get('score')

        for i in self.meta_ratings:
            try:
                name = i['source']
            except KeyError:
                continue
            if i.get('value'):
                ratings[self.ratings_translation.get(name) or f'{name}_rating'] = i['value']
            if i.get('votes'):
                ratings[f'{name}_votes'] = i['votes']

        self._ratings = ratings
        return self._ratings


class MDbList(RequestAPI):

    api_key = API_KEY

    def __init__(self, api_key=None):
        api_key = api_key or self.api_key

        super(MDbList, self).__init__(
            req_api_key=f'apikey={api_key}',
            req_api_name='MDbList.v2',
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

    def get_list_of_lists(self, path, page=1, limit: int = None):
        response = self.get_request_sc(path, cache_refresh=True if page == 1 else False)
        response = MDbListPaginationLists(response, page=page, limit=limit or 250)
        return response.items if not response.next_page else response.items + response.next_page

    def get_list_of_lists_search(self, query):
        return self.get_list_of_lists(path=f'lists/search?query={query}')

    def get_custom_trakt_style_list(self, list_id):
        path = f'lists/{list_id}/items'
        response = self.get_request_sc(path, cache_refresh=True)
        return self.get_paginated(response, permitted_types=('movie', 'show'), trakt_style=True)

    def get_custom_list(self, list_id, page=1, limit: int = None):
        path = f'lists/{list_id}/items'
        response = self.get_request_sc(path, cache_refresh=True if page == 1 else False)
        response = self.get_paginated(response, page=page, limit=limit)
        return response

    def get_paginated(self, response, page=1, limit: int = None, permitted_types: tuple = None, trakt_style=False):
        return ItemListPagination(response or {}, page=page, limit=limit, permitted_types=permitted_types, trakt_style=trakt_style)
