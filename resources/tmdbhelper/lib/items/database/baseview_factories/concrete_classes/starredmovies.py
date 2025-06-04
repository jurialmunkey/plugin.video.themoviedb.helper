from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class StarredMoviesMediaList(MediaList):
    table = 'castmember'
    cached_data_innertable = 'movie'

    @property
    def cached_data_base_conditions(self):  # WHERE conditions
        return f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '

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
    def group_by(self):
        return f'{self.table}.parent_id'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time, DATALEVEL_MAX)

    cached_data_check_key = 'tmdb_id'
    item_mediatype = 'movie'
    item_tmdb_type = 'movie'
    item_label_key = 'title'
    item_alter_key = 'role'

    @property
    def filter_key_map(self):
        return {
            'role': f'{self.cached_data_innertable}.role',
            'character': f'{self.cached_data_innertable}.role',
            'title': f'{self.cached_data_innertable}.title',
            'year': f'{self.cached_data_innertable}.year',
            'premiered': f'{self.cached_data_innertable}.premiered',
            'status': f'{self.cached_data_innertable}.status',
            'votes': f'{self.cached_data_innertable}.votes',
            'rating': f'{self.cached_data_innertable}.rating',
            'popularity': f'{self.cached_data_innertable}.popularity',
        }

    sort_direction = {
        'title': 'ASC'
    }

    sort_by_fallback = 'votes'
    order_by_direction_fallback = 'DESC'

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
