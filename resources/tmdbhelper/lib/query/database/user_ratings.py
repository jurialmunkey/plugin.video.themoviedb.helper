from jurialmunkey.ftools import cached_property


RATINGS_EXPIRY = 60 * 60 * 6


class UserRatingsRequest:
    def __init__(self, query_database):
        self.query_database = query_database

    @property
    def tmdb_user_api(self):
        return self.query_database.tmdb_user_api

    @property
    def get_response_json(self):
        return self.tmdb_user_api.get_authorised_response_json_v3

    @property
    def format_authorised_path(self):
        return self.tmdb_user_api.format_authorised_path

    @cached_property
    def results_movies(self):
        return self.get_results(self.get_account_response('movies'))

    @cached_property
    def results_tvshows(self):
        return self.get_results(self.get_account_response('tv'))

    @cached_property
    def results_episodes(self):
        return self.get_results(self.get_account_response('tv/episodes'))

    def get_results(self, data):
        try:
            return data['results'] or []
        except (KeyError, TypeError):
            return []

    def get_account_response(self, endpoint):
        path = f'account/{{account_id}}/rated/{endpoint}'
        path = self.format_authorised_path(path)
        return self.get_response_json(path)

    def thread_requests(self):
        from tmdbhelper.lib.addon.thread import ParallelThread

        def get_results_attribute(i):
            return getattr(self, i)

        attributes = (
            'results_movies',
            'results_tvshows',
            'results_episodes'
        )

        with ParallelThread(attributes, get_results_attribute):
            pass

    @cached_property
    def values(self):
        self.thread_requests()

        values = []
        values += [
            (i['id'], 'movie', -1, -1, i['rating'] * 10)
            for i in self.results_movies
        ]
        values += [
            (i['id'], 'tv', -1, -1, i['rating'] * 10)
            for i in self.results_tvshows
        ]
        values += [
            (i['show_id'], 'tv', i['season_number'], i['episode_number'], i['rating'] * 10)
            for i in self.results_episodes
        ]

        return values


class FindQueriesDatabaseUserRatings:

    user_ratings_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'tmdb_type': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'season': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'episode': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'rating': {
            'data': 'INTEGER'
        },
    }

    """
    user_ratings
    """

    def get_user_ratings(self, tmdb_type, tmdb_id, season=None, episode=None, forced=False):
        from jurialmunkey.parser import try_int
        table = 'user_ratings'
        keys = ('tmdb_id', 'tmdb_type', 'season', 'episode', 'rating')

        def configure_rating(data):
            try:
                return data[0]['rating']
            except (KeyError, TypeError, IndexError):
                return

        def get_cached():
            return self.get_cached_values(
                table, keys, configure_rating,
                conditions='tmdb_id=? AND tmdb_type=? AND season=? AND episode=?',
                values=(
                    try_int(tmdb_id),
                    tmdb_type,
                    try_int(season, fallback=-1),
                    try_int(episode, fallback=-1)
                ),
            )

        def set_cached():
            if not forced and not self.is_expired(table):
                return
            values = UserRatingsRequest(self).values
            if not values:
                return
            self.set_cached_values(table, keys, values, expiry=RATINGS_EXPIRY)
            return get_cached()

        return set_cached() if forced else get_cached() or set_cached()
