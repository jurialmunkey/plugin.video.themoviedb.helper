from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MAX


class SeriesMoviesMediaList(MediaList):
    table = 'collection'

    cached_data_table = (
        'baseitem '
        'INNER JOIN collection ON collection.id = baseitem.id '
        'INNER JOIN movie ON movie.collection_id = collection.id'
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
    def cached_data_conditions_base(self):  # WHERE conditions
        return (
            f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '
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

    filter_key_map = {
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
        'rating': 'rating',
        'votes': 'votes',
        'premiered': 'premiered',
        'year': 'year',
        'title': 'title',
    }

    # Since our default sort is year ASC unlike most with DESC we need to map DESC instead
    sort_how_map = {
        'popularity': 'DESC',
        'rating': 'DESC',
        'votes': 'DESC'
    }

    @property
    def cached_data_conditions_sort(self):
        """ ORDER BY """
        try:
            return f'movie.{self.sort_key_map[self.sort_by]} {self.cached_data_conditions_how}'
        except (KeyError, TypeError, NameError):
            return self.cached_data_conditions_sort_fallback

    @property
    def cached_data_conditions_sort_fallback(self):
        return f'year {self.cached_data_conditions_how}'

    @property
    def cached_data_conditions_how(self):
        try:
            return self.sort_how or self.sort_how_map[self.sort_by]
        except (KeyError, TypeError, NameError):
            return self.sort_how or 'ASC'

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'popularity': i['popularity'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'movie',
        }


class Series(SeriesMoviesMediaList):
    pass
