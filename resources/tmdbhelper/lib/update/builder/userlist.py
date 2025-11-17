from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.builder.media import LibraryBuilder


"""
IMPORTANT: These limits are set to prevent excessive API data usage.
Please respect the APIs that provide this data for free.
"""
LIBRARY_ADD_LIMIT_TVSHOWS = 500
LIBRARY_ADD_LIMIT_MOVIES = 2500


class LibraryBuilderUserList(LibraryBuilder):

    @cached_property
    def all_tvshows(self):
        return self.get_all_of_type('show')

    @cached_property
    def all_movies(self):
        return self.get_all_of_type('movie')

    def get_all_of_type(self, item_type):
        return [i[item_type] for i in self.request if i.get('type') == item_type]

    """
    Limits
    """

    @property
    def len_movies(self):
        return len(self.all_movies)

    @property
    def len_tvshows(self):
        return len(self.all_tvshows)

    @property
    def len_all_items(self):
        return (self.len_movies + self.len_tvshows)

    @property
    def is_overlimit(self):
        if self.len_movies > LIBRARY_ADD_LIMIT_MOVIES:
            return True
        if self.len_tvshows > LIBRARY_ADD_LIMIT_TVSHOWS:
            return True
        return False

    """
    Confirmation
    """

    confirm = 1

    @cached_property
    def is_confirmed(self):
        from xbmcgui import Dialog
        from tmdbhelper.lib.addon.plugin import get_localized

        if self.is_overlimit:
            Dialog().ok(get_localized(32125), '\n'.join([
                get_localized(32168).format(self.list_slug, self.user_slug),
                get_localized(32170).format(self.len_tvshows, self.len_movies),
                '',
                get_localized(32164).format(LIBRARY_ADD_LIMIT_TVSHOWS, LIBRARY_ADD_LIMIT_MOVIES)
            ])) if self.confirm else None
            return False

        if self.confirm and self.len_all_items >= self.confirm:
            return Dialog().yesno(get_localized(32125), '\n'.join([
                get_localized(32168).format(self.list_slug, self.user_slug),
                get_localized(32171).format(self.len_all_items) if self.len_all_items > 20 else '',
                '',
                get_localized(32126)
            ]))

        return True

    """
    Request
    """

    @cached_property
    def mdblist_apikey(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return get_setting('mdblist_apikey', 'str')

    @cached_property
    def request_func(self):
        if self.user_slug != '__api_mdblist__':
            from tmdbhelper.lib.api.trakt.api import TraktAPI
            return TraktAPI().get_response_json
        if self.mdblist_apikey:
            from tmdbhelper.lib.api.mdblist.api import MDbList
            return MDbList().get_response
        return lambda *args, **kwgs: None

    @property
    def request_args(self):
        if self.user_slug == '__api_mdblist__':
            return ('lists', self.list_slug, 'items')
        if self.list_slug.startswith('watchlist'):
            return ('users', self.user_slug, self.list_slug)
        return ('users', self.user_slug, 'lists', self.list_slug, 'items')

    def request_configure(self, request):
        if not request:
            return
        if self.user_slug != '__api_mdblist__':
            return request
        request = request.json()
        request = request.get('movies', []) + request.get('shows', [])
        return [j for j in (self.request_configure_mdblist_item(i) for i in request) if j]

    @staticmethod
    def request_configure_mdblist_item(item):
        try:
            mediatype = item['mediatype']
            return {
                'type': mediatype,
                mediatype: {
                    'title': item['title'],
                    'ids': {
                        'tmdb': item['id'],
                        'imdb': item['imdb_id']
                    }
                }
            }
        except (KeyError, TypeError):
            return

    @cached_property
    def request(self):
        request = self.request_func(*self.request_args)
        request = self.request_configure(request)
        return request

    """
    Build
    """

    @cached_property
    def builder_tvshows(self):
        from tmdbhelper.lib.update.builder.tvshows import LibraryBuilderTvshows
        return self.get_builder(LibraryBuilderTvshows())

    @cached_property
    def builder_movies(self):
        from tmdbhelper.lib.update.builder.movies import LibraryBuilderMovies
        return self.get_builder(LibraryBuilderMovies())

    def create(self, user_slug, list_slug, **kwargs):
        self.user_slug = user_slug
        self.list_slug = list_slug
        if not self.request:
            return
        if not self.is_confirmed:
            return
        self.add_library_items(self.all_movies, self.builder_movies)
        self.add_library_items(self.all_tvshows, self.builder_tvshows)

    def add_library_items(self, items, builder):
        from tmdbhelper.lib.addon.plugin import get_localized
        total = len(items)
        for count, item in enumerate(items):
            try:
                name = item['title']
                tmdb = item['ids']['tmdb']
                imdb = item['ids']['imdb']
            except AttributeError:
                continue
            self.dialog_msg(count, total, message=f'{get_localized(32167)} {name}')
            builder.create(tmdb_id=tmdb, imdb_id=imdb)
