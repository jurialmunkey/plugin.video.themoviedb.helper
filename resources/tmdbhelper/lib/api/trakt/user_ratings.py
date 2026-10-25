from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.consts import TRAKT_MAX_ITEMS_PER_PAGE


class TraktUserRating:
    def __init__(self, trakt_api, item_type, trakt_id):
        self.trakt_api = trakt_api
        self.item_type = item_type
        self.trakt_id = trakt_id

    @cached_property
    def rating(self):
        return self.get_rating()

    def get_rating(self):
        return next((item['rating'] for page in self.get_pages() for item in page
                     if item[self.item_type]['ids']['trakt'] == self.trakt_id), None)

    def get_pages(self):
        page = 1
        while True:
            response = self.trakt_api.get_response(
                'sync', 'ratings', f'{self.item_type}s', page=page, limit=TRAKT_MAX_ITEMS_PER_PAGE)
            if response is None or response.status_code != 200:
                return
            try:
                data = response.json()
            except ValueError:
                return
            yield data
            if page >= try_int(response.headers.get('x-pagination-page-count'), fallback=1):
                return
            page += 1
