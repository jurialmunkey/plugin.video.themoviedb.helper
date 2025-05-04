from tmdbhelper.lib.files.ftools import cached_property


class TMDbDatabaseGenres:

    genres_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
        'tmdb_type': {
            'data': 'TEXT',
        },
    }

    """
    genres
    """

    @cached_property
    def genres(self):
        return self.get_genres()

    def get_genres(self, tmdb_type=None):
        table = 'genres'
        keys = ('name', 'id', 'tmdb_type')

        def get_genres(tmdb_type):
            genres = self.tmdb_api.get_response_json('genre', tmdb_type, 'list') or {}
            genres = genres.get('genres')
            return {i['name']: i['id'] for i in genres if i} if genres else {}

        def configure_genre_dict(genres):
            return {i['name']: i['id'] for i in genres} if genres else {}

        def get_cached():
            kwgs = {'values': (tmdb_type,), 'conditions': 'tmdb_type=?'} if tmdb_type else {}
            return self.get_cached_values(table, keys, configure_genre_dict, **kwgs)

        def set_cached():
            data = {}
            data['tv'] = get_genres('tv')
            data['movie'] = get_genres('movie')
            if not data:
                return
            values = [(name, tmdb_id, tmdb_type) for tmdb_type, i in data.items() for name, tmdb_id in i.items()]
            self.set_cached_values(table, keys, values)
            return get_cached()

        return get_cached() or set_cached()
