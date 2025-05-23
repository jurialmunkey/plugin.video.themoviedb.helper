from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes


class Movie(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.playcount,
    )

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbclist_routes,
            (('studio', None), 'name', 'studio'),
        )

    def get_infolabels_special(self, infolabels):
        try:
            infolabels['set'] = self.data[0]['collection_title']
        except (TypeError, KeyError, IndexError):
            pass
        return infolabels

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        infoproperties = self.get_infoproperties_progress(infoproperties)
        infoproperties = self.get_infoproperties_lastplayed(infoproperties)
        infoproperties = self.get_infoproperties_ranks(infoproperties)
        infoproperties = self.get_infoproperties_collection(infoproperties)
        return infoproperties

    def get_infoproperties_collection(self, infoproperties):
        collection_id = self.get_data_value('collection_id')

        if not collection_id:
            return infoproperties

        try:
            from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
            tmdb_imagepath = TMDbImagePath()
            infoproperties['set.title'] = infoproperties['set.name'] = self.data[0]['collection_title']
            infoproperties['set.tmdb_id'] = self.data[0]['collection_tmdb_id']
            infoproperties['set.poster'] = tmdb_imagepath.get_imagepath_poster(self.data[0]['collection_poster'])
            infoproperties['set.fanart'] = tmdb_imagepath.get_imagepath_fanart(self.data[0]['collection_fanart'])
        except (TypeError, KeyError, IndexError):
            pass

        data_list = self.parent_db_cache.get_cached_list_values(
            table='movie',
            keys=(
                'ROUND(AVG(rating), 1) as rating',
                'SUM(votes) as votes',
                'COUNT(movie.tmdb_id) as numitems',
                'MAX(year) as year_last',
                'MIN(year) as year_first',
            ),
            values=(collection_id,),
            conditions='movie.collection_id=? GROUP BY movie.collection_id')

        infoproperties['set.rating'] = data_list[0]['rating']
        infoproperties['set.votes'] = data_list[0]['votes']
        infoproperties['set.numitems'] = data_list[0]['numitems']
        infoproperties['set.year.last'] = data_list[0]['year_last']
        infoproperties['set.year.first'] = data_list[0]['year_first']
        infoproperties['set.years'] = f"{data_list[0]['year_first']} - {data_list[0]['year_last']}"

        if not self.parent_db_cache.extendedinfo:
            return infoproperties

        data_keys = (
            'title', 'year', 'plot', 'duration', 'premiered', 'status',
            'rating', 'votes', 'popularity', 'tmdb_id', 'originaltitle',
        )
        data_list = self.parent_db_cache.get_cached_list_values(
            table='movie',
            keys=data_keys,
            values=(collection_id,),
            conditions='movie.collection_id=? ORDER BY year')

        for x, i in enumerate(data_list, 1):
            for k in data_keys:
                infoproperties[f'set.{x}.{k}'] = i[k]

        return infoproperties
