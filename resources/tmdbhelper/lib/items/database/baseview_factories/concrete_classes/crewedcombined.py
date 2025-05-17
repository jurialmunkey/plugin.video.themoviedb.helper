from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredcombined import StarredCombinedMediaList


class CrewedCombinedMediaList(StarredCombinedMediaList):
    table = 'crewmember'

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
            'parent_id',
            'GROUP_CONCAT(role, " / ") as role',
            'GROUP_CONCAT(department, " / ") as department',
            f'IFNULL(movie.tmdb_id, tvshow.tmdb_id) as tmdb_id',
            f'IFNULL(movie.title, tvshow.title) as title',
            f'IFNULL(movie.year, tvshow.year) as year',
            f'IFNULL(movie.premiered, tvshow.premiered) as premiered',
            f'IFNULL(movie.status, tvshow.status) as status',
            f'IFNULL(movie.votes, tvshow.votes) as votes',
            f'IFNULL(movie.rating, tvshow.rating) as rating',
            f'IFNULL(movie.popularity, tvshow.popularity) as popularity'
        )


class Person(CrewedCombinedMediaList):
    pass
