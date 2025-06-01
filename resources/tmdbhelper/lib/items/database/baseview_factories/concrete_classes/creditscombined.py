from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredcombined import StarredCombinedMediaList


class CreditsCombinedMediaList(StarredCombinedMediaList):

    cached_data_table = """
        baseitem
        INNER JOIN person ON baseitem.id = person.id
        LEFT JOIN castmember ON person.tmdb_id = castmember.tmdb_id
        LEFT JOIN crewmember ON person.tmdb_id = crewmember.tmdb_id
        LEFT JOIN movie ON movie.id = IFNULL(castmember.parent_id, crewmember.parent_id)
        LEFT JOIN tvshow ON tvshow.id = IFNULL(castmember.parent_id, crewmember.parent_id)
    """

    @property
    def cached_data_conditions_base(self):  # WHERE conditions
        return (
            'person.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '
            'AND IFNULL(movie.id, tvshow.id) IS NOT NULL '
            'GROUP BY IFNULL(movie.id, tvshow.id) '
            f'ORDER BY {self.cached_data_conditions_sort}'
        )

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
            'IFNULL(movie.id, tvshow.id) as parent_id',
            'GROUP_CONCAT(DISTINCT IFNULL(castmember.role, crewmember.role)) as role',
            'GROUP_CONCAT(DISTINCT crewmember.department) as department',
            'IFNULL(movie.tmdb_id, tvshow.tmdb_id) as tmdb_id',
            'IFNULL(movie.title, tvshow.title) as title',
            'IFNULL(movie.year, tvshow.year) as year',
            'IFNULL(movie.premiered, tvshow.premiered) as premiered',
            'IFNULL(movie.status, tvshow.status) as status',
            'IFNULL(movie.votes, tvshow.votes) as votes',
            'IFNULL(movie.rating, tvshow.rating) as rating',
            'IFNULL(movie.popularity, tvshow.popularity) as popularity'
        )


class Person(CreditsCombinedMediaList):
    pass
