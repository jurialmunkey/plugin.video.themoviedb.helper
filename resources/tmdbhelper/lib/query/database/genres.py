from jurialmunkey.ftools import cached_property


GENRE_TYPES = {
    'movie': 0b01,
    'tv': 0b10,
    'both': 0b11,
}


class FindQueriesDatabaseGenres:

    genres_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
        'type': {
            'data': 'INTEGER DEFAULT 0 NOT NULL',  # Use binary 0b00=None, 0b01=Movie, 0b10=TV, 0b11=Both
            'indexed': True
        },
    }

    """
    genres
    """

    @cached_property
    def genres(self):
        return self.get_genres()

    def get_genres(self, tmdb_type='both'):
        table = 'genres'
        keys = ('id', 'name', 'type')

        def get_genres(tmdb_type):
            genres = self.tmdb_api.get_response_json('genre', tmdb_type, 'list') or {}
            genres = genres.get('genres')
            return {i['id']: i['name'] for i in genres if i} if genres else {}

        def configure_genre_dict(genres):
            return {i['name']: i['id'] for i in genres} if genres else {}

        def get_cached():
            kwgs = {'values': (GENRE_TYPES[tmdb_type], GENRE_TYPES['both']), 'conditions': 'type=? OR type=? ORDER BY name'} if tmdb_type else {}
            return self.get_cached_values(table, keys, configure_genre_dict, **kwgs)

        def set_cached():
            genres_tv = get_genres('tv')
            genres_movies = get_genres('movie')
            genres_both = set(genres_tv).intersection(genres_movies)
            values = [
                (
                    tmdb_id,  # ID
                    genres_movies.get(tmdb_id) or genres_tv.get(tmdb_id),  # NAME
                    (
                        GENRE_TYPES['both']
                        if tmdb_id in genres_both else
                        GENRE_TYPES['tv']
                        if tmdb_id in genres_tv else
                        GENRE_TYPES['movie']
                    ),  # TYPE
                )
                for tmdb_id in set().union(genres_tv, genres_movies)
            ]
            self.set_cached_values(table, keys, values)
            return get_cached()

        return get_cached() or set_cached()
