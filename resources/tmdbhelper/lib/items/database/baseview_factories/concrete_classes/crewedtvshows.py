from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.crewedmovies import CrewedMoviesMediaList


class CrewedTvshowsMediaList(CrewedMoviesMediaList):
    cached_data_innertable = 'tvshow'

    @property
    def cached_data_base_conditions(self):  # WHERE conditions
        return f'{self.table}.tmdb_id=? AND baseitem.expiry>=? AND baseitem.datalevel>=? '

    @property
    def group_by(self):
        return f'{self.table}.parent_id'

    sort_by_fallback = 'appearances'

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
            'job': i['role'],
            'department': i['department'],
            'popularity': i['popularity'],
            'episodes': i['appearances'],
            'tmdb_id': i['tmdb_id'],
            'tmdb_type': 'tv',
        }

    @property
    def cached_data_keys(self):
        return super().cached_data_keys + ('appearances', )


class Person(CrewedTvshowsMediaList):
    pass
