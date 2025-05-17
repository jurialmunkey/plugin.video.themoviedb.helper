from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class StarredMoviesMediaList(MediaList):
    table = 'castmember'
    cached_data_innertable = 'movie'

    @property
    def cached_data_table(self):
        return (
            'baseitem '
            'INNER JOIN person ON person.id = baseitem.id '
            f'INNER JOIN {self.table} ON {self.table}.tmdb_id = person.tmdb_id '
            f'INNER JOIN {self.cached_data_innertable} ON {self.cached_data_innertable}.id = {self.table}.parent_id'
        )

    @property
    def cached_data_keys(self):
        return (
            'GROUP_CONCAT(role, " / ") as role',
            f'{self.cached_data_innertable}.tmdb_id AS tmdb_id',
            f'{self.cached_data_innertable}.title',
            f'{self.cached_data_innertable}.year',
            f'{self.cached_data_innertable}.premiered',
            f'{self.cached_data_innertable}.status',
            f'{self.cached_data_innertable}.votes',
            f'{self.cached_data_innertable}.rating',
            f'{self.cached_data_innertable}.popularity'
        )

    @property
    def cached_data_conditions_base(self):  # WHERE conditions
        return (
            f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '
            f'GROUP BY {self.table}.parent_id '
            f'ORDER BY {self.cached_data_conditions_sort}'
        )

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time, DATALEVEL_MAX)

    cached_data_check_key = 'tmdb_id'
    item_mediatype = 'movie'
    item_tmdb_type = 'movie'
    item_label_key = 'title'
    item_alter_key = 'role'

    filter_key_map = {
        'role': 'role',
        'character': 'role',
        'title': 'title',
        'year': 'year',
        'premiered': 'premiered',
        'status': 'status',
        'votes': 'votes',
        'rating': 'rating',
        'popularity': 'popularity',
    }

    sort_key_map = {
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

    @property
    def cached_data_conditions_sort(self):
        """ ORDER BY """
        try:
            return f'{self.cached_data_innertable}.{self.sort_key_map[self.sort_by]} {self.cached_data_conditions_how}'
        except (KeyError, TypeError, NameError):
            return self.cached_data_conditions_sort_fallback

    @property
    def cached_data_conditions_sort_fallback(self):
        return f'votes {self.cached_data_conditions_how}'

    @property
    def cached_data_conditions_how(self):
        try:
            return self.sort_how or self.sort_how_map[self.sort_by]
        except (KeyError, TypeError, NameError):
            return self.sort_how or 'DESC'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'character': i['role'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }


class Person(StarredMoviesMediaList):
    pass
