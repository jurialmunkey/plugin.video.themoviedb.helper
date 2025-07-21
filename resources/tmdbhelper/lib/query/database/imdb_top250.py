from jurialmunkey.ftools import cached_property


class FindQueriesDatabaseIMDbTop250:

    imdb_top250_columns = {
        'rank': {
            'data': 'INTEGER',
            'unique': True,
        },
        'tmdb_type': {
            'data': 'TEXT',
            'unique': True,
            'indexed': True,
        },
        'tmdb_id': {
            'data': 'INTEGER'
        },
        'title': {
            'data': 'TEXT'
        },
        'year': {
            'data': 'INTEGER'
        },
        'slug': {
            'data': 'TEXT'
        },
    }

    """
    imdb_top250
    """

    @cached_property
    def imdb_top250_movie(self):
        return self.get_imdb_top250('movie')

    @cached_property
    def imdb_top250_tv(self):
        return self.get_imdb_top250('tv')

    def get_imdb_top250_list_cached(self, tmdb_type):
        if tmdb_type == 'movie':
            return self. imdb_top250_movie
        if tmdb_type == 'tv':
            return self. imdb_top250_tv

    def get_imdb_top250(self, tmdb_type, output_key='tmdb_id'):
        table = 'imdb_top250'

        def mapping_function(data):
            return [i[output_key] for i in data] if data else []

        def get_cached():
            kwgs = {'values': (tmdb_type,), 'conditions': 'tmdb_type=? ORDER BY rank ASC'} if tmdb_type else {}
            return self.get_cached_values(table, (output_key, ), mapping_function, **kwgs)

        def set_cached():
            sync = GetIMDbTop250Request(tmdb_type, self.trakt_api)
            if not sync.values:
                return
            self.set_cached_values(table, sync.keys, sync.values)
            return get_cached()

        return get_cached() or set_cached()


class GetIMDbTop250MoviesRequest:
    url = 'users/justin/lists/imdb-top-rated-movies/items'
    tmdb_type = 'movie'
    item_type = 'movie'
    columns = FindQueriesDatabaseIMDbTop250.imdb_top250_columns

    def __init__(self, trakt_api):
        self.trakt_api = trakt_api

    @cached_property
    def keys(self):
        return tuple(self.columns.keys())

    @cached_property
    def response(self):
        return self.trakt_api.get_response(self.url, limit=4095)

    @cached_property
    def response_json(self):
        return self.response.json() if self.response else None

    @cached_property
    def values(self):
        return [
            tuple([i[k] for k in self.keys])
            for i in self.items
        ]

    @cached_property
    def items(self):
        return [
            {
                'rank': i['rank'],
                'tmdb_type': self.tmdb_type,
                'tmdb_id': i[self.item_type]['ids']['tmdb'],
                'title': i[self.item_type]['title'],
                'year': i[self.item_type]['year'],
                'slug': i[self.item_type]['ids']['slug'],
            }
            for i in self.response_json
        ] if self.response_json else []


class GetIMDbTop250TVShowsRequest(GetIMDbTop250MoviesRequest):
    url = 'users/justin/lists/imdb-top-rated-tv-shows/items'
    tmdb_type = 'tv'
    item_type = 'show'


def GetIMDbTop250Request(tmdb_type, *args, **kwargs):
    if tmdb_type == 'movie':
        return GetIMDbTop250MoviesRequest(*args, **kwargs)
    if tmdb_type == 'tv':
        return GetIMDbTop250TVShowsRequest(*args, **kwargs)
