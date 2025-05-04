from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


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
            f'{self.table}.tmdb_id=? AND baseitem.expiry>=? '
            f'GROUP BY {self.table}.parent_id '
            f'ORDER BY {self.cached_data_innertable}.votes DESC'
        )

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time)

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

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'chracter': i['role'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }


class Person(StarredMoviesMediaList):
    pass
