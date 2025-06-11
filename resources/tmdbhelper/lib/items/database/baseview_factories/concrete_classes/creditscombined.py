from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredcombined import StarredCombinedMediaList


class CreditsCombinedMediaList(StarredCombinedMediaList):

    cached_data_table = """
        baseitem INNER JOIN person ON person.id = baseitem.id
        INNER JOIN
        (
            SELECT tmdb_id, role, appearances, 'Acting' as department, parent_id
            FROM castmember
            UNION
            SELECT tmdb_id, role, appearances, department, parent_id
            FROM crewmember
        ) credits ON credits.tmdb_id = person.tmdb_id
        INNER JOIN
        (
            SELECT tmdb_id, title, year, premiered, status, votes, rating, popularity, id, "movie" as tmdb_type, "movie" as mediatype
            FROM movie
            UNION
            SELECT tmdb_id, title, year, premiered, status, votes, rating, popularity, id, "tv" as tmdb_type, "tvshow" as mediatype
            FROM tvshow
        ) media ON media.id = credits.parent_id
    """

    cached_data_base_conditions = """
        person.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=?
    """

    group_by = 'media.id'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'job': i['role'],
            'department': i['department'],
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': i['tmdb_type'],
        }

    @property
    def cached_data_keys(self):
        return (
            'media.id as parent_id',
            'media.tmdb_id as tmdb_id',
            'media.tmdb_type as tmdb_type',
            'media.mediatype as mediatype',
            'media.title as title',
            'media.year as year',
            'media.premiered as premiered',
            'media.status as status',
            'media.votes as votes',
            'media.rating as rating',
            'media.popularity as popularity',
            'GROUP_CONCAT(DISTINCT credits.role) as role',
            'GROUP_CONCAT(DISTINCT credits.department) as department',
        )


class Person(CreditsCombinedMediaList):
    pass
