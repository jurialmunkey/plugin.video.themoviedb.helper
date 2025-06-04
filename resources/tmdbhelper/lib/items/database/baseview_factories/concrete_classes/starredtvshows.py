from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.starredmovies import StarredMoviesMediaList


class StarredTvshowsMediaList(StarredMoviesMediaList):
    cached_data_innertable = 'tvshow'

    @property
    def group_by(self):
        return f'{self.table}.parent_id'

    sort_by_fallback = 'appearances'
    order_by_direction_fallback = 'DESC'

    item_mediatype = 'tvshow'
    item_tmdb_type = 'tv'

    @property
    def filter_key_map(self):
        filter_key_map = super().filter_key_map.copy()
        filter_key_map['appearances'] = 'appearances'
        filter_key_map['episodes'] = 'appearances'
        return filter_key_map

    @staticmethod
    def map_item_infoproperties(i):
        return {
            'role': i['role'],
            'character': i['role'],
            'popularity': i['popularity'],
            'episodes': i['appearances'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'tv',
        }

    @property
    def cached_data_keys(self):
        return super().cached_data_keys + ('appearances', )


class Person(StarredTvshowsMediaList):
    pass
