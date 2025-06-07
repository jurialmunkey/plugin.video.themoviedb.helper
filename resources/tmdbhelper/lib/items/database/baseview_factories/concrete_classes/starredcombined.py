from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class StarredCombinedMediaList(MediaList):
    table = 'castmember'

    @property
    def cached_data_table(self):
        return """
        baseitem INNER JOIN person ON person.id = baseitem.id
        INNER JOIN {table} ON {table}.tmdb_id = person.tmdb_id
        INNER JOIN
        (
            SELECT tmdb_id, title, year, premiered, status, votes, rating, popularity, id, "movie" as tmdb_type, "movie" as mediatype
            FROM movie
            UNION
            SELECT tmdb_id, title, year, premiered, status, votes, rating, popularity, id, "tv" as tmdb_type, "tvshow" as mediatype
            FROM tvshow
        ) media ON media.id = {table}.parent_id
        """.format(table=self.table)

    group_by = 'media.id'

    cached_data_keys = (
        'media.id as parent_id',
        'GROUP_CONCAT(role, " / ") as role',
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
    )

    @property
    def cached_data_base_conditions(self):
        return f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=?'

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time, DATALEVEL_MAX)

    cached_data_check_key = 'tmdb_id'
    item_mediatype = ''
    item_tmdb_type = ''
    item_label_key = 'title'
    item_alter_key = 'role'

    filter_key_map = {
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
        }

    def map_item_params(self, i):
        return {
            'info': 'details',
            'tmdb_type': i['tmdb_type'],
            'tmdb_id': i['tmdb_id'],
        }

    def map_mediatype(self, i):
        return i['mediatype']


class Person(StarredCombinedMediaList):
    pass
