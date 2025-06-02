from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class StarredCombinedMediaList(MediaList):
    table = 'castmember'

    @property
    def cached_data_table(self):
        return (
            'baseitem '
            'INNER JOIN person ON person.id = baseitem.id '
            f'INNER JOIN {self.table} ON {self.table}.tmdb_id = person.tmdb_id '
            f'LEFT JOIN movie ON movie.id = {self.table}.parent_id '
            f'LEFT JOIN tvshow ON tvshow.id = {self.table}.parent_id'
        )

    @property
    def cached_data_keys(self):
        return (
            'parent_id',
            'GROUP_CONCAT(role, " / ") as role',
            f'IFNULL(movie.tmdb_id, tvshow.tmdb_id) as tmdb_id',
            f'IFNULL(movie.title, tvshow.title) as title',
            f'IFNULL(movie.year, tvshow.year) as year',
            f'IFNULL(movie.premiered, tvshow.premiered) as premiered',
            f'IFNULL(movie.status, tvshow.status) as status',
            f'IFNULL(movie.votes, tvshow.votes) as votes',
            f'IFNULL(movie.rating, tvshow.rating) as rating',
            f'IFNULL(movie.popularity, tvshow.popularity) as popularity'
        )

    @property
    def cached_data_base_conditions(self):  # WHERE conditions
        return (
            f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '
            'AND IFNULL(movie.id, tvshow.id) IS NOT NULL '
        )

    @property
    def group_by(self):
        return f'{self.table}.parent_id'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time, DATALEVEL_MAX)

    cached_data_check_key = 'tmdb_id'
    item_mediatype = ''
    item_tmdb_type = ''
    item_label_key = 'title'
    item_alter_key = 'role'

    filter_key_map = {}

    sort_by_map = {
        'popularity': 'popularity',
        'vote_average': 'rating',
        'rating': 'rating',
        'vote_count': 'votes',
        'votes': 'votes',
        'release_date': 'premiered',
        'first_air_date': 'premiered',
        'premiered': 'premiered',
        'year': 'year',
        'title': 'title',
    }

    sort_how_map = {
        'title': 'ASC'
    }

    order_by_fallback = 'votes'
    order_how_fallback = 'DESC'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'character': i['role'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }

    def map_item_params(self, i):
        return {
            'info': 'details',
            'tmdb_type': 'movie' if self.map_mediatype(i) == 'movie' else 'tv',
            'tmdb_id': i['tmdb_id'],
        }

    def map_mediatype(self, i):
        if i['parent_id'].startswith('movie'):
            return 'movie'
        return 'tvshow'


class Person(StarredCombinedMediaList):
    pass
