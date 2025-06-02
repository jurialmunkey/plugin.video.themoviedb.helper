from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class SeriesMoviesMediaList(MediaList):
    table = 'collection'

    cached_data_table = (
        'baseitem '
        'INNER JOIN collection ON collection.id = baseitem.id '
        'INNER JOIN belongs ON belongs.parent_id = collection.id '
        'INNER JOIN movie ON movie.id = belongs.id '
    )

    cached_data_keys = (
        'movie.tmdb_id AS tmdb_id',
        'movie.title',
        'movie.year',
        'movie.premiered',
        'movie.status',
        'movie.votes',
        'movie.rating',
        'movie.popularity'
    )

    @property
    def cached_data_base_conditions(self):  # WHERE conditions
        return f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '

    @property
    def cached_data_values(self):
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.tmdb_id, self.current_time, DATALEVEL_MAX)

    cached_data_check_key = 'tmdb_id'
    item_mediatype = 'movie'
    item_tmdb_type = 'movie'
    item_label_key = 'title'

    filter_key_map = {
        'title': 'movie.title',
        'year': 'movie.year',
        'premiered': 'movie.premiered',
        'status': 'movie.status',
        'votes': 'movie.votes',
        'rating': 'movie.rating',
        'popularity': 'movie.popularity',
    }

    # Since our default sort is year ASC unlike most with DESC we need to map DESC instead
    sort_direction = {
        'popularity': 'DESC',
        'rating': 'DESC',
        'votes': 'DESC'
    }

    sort_by_fallback = 'year'
    order_by_direction_fallback = 'ASC'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }


class Series(SeriesMoviesMediaList):
    pass
