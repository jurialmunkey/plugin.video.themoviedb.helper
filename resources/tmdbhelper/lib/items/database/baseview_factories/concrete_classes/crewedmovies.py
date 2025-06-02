from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredmovies import StarredMoviesMediaList


class CrewedMoviesMediaList(StarredMoviesMediaList):
    table = 'crewmember'

    item_mediatype = 'movie'
    item_tmdb_type = 'movie'

    filter_key_map = sort_key_map = {
        'job': 'role',
        'role': 'role',
        'department': 'department',
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
            'job': i['role'],
            'department': i['department'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }

    @property
    def cached_data_keys(self):
        return (
            'GROUP_CONCAT(role, " / ") as role',
            'GROUP_CONCAT(department, " / ") as department',
            f'{self.cached_data_innertable}.tmdb_id AS tmdb_id',
            f'{self.cached_data_innertable}.title',
            f'{self.cached_data_innertable}.year',
            f'{self.cached_data_innertable}.premiered',
            f'{self.cached_data_innertable}.status',
            f'{self.cached_data_innertable}.votes',
            f'{self.cached_data_innertable}.rating',
            f'{self.cached_data_innertable}.popularity'
        )


class Person(CrewedMoviesMediaList):
    pass
