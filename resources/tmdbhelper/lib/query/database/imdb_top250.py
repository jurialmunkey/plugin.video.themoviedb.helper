from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.providers.imdb_top250 import IMDbTop250


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
            items = IMDbTop250(tmdb_type).items
            if not items:
                return
            keys = tuple(self.imdb_top250_columns)
            values = [tuple(item[key] for key in keys) for item in items]
            self.set_cached_values(table, keys, values)
            return get_cached()

        return get_cached() or set_cached()
