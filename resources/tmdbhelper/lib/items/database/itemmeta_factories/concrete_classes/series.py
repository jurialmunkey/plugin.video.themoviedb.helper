from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem


class SeriesItem:
    def get_infoproperties_collection(self, infoproperties):

        if self.collection_id:

            data_list = self.return_basemeta_db('series_stats')

            try:
                infoproperties['set.rating'] = data_list.cached_data[0]['rating']
                infoproperties['set.votes'] = data_list.cached_data[0]['votes']
                infoproperties['set.numitems'] = data_list.cached_data[0]['numitems']
                infoproperties['set.year.last'] = data_list.cached_data[0]['year_last']
                infoproperties['set.year.first'] = data_list.cached_data[0]['year_first']
                infoproperties['set.years'] = f"{infoproperties['set.year.first']} - {infoproperties['set.year.last']}"
            except IndexError:
                pass

            data_list = self.return_basemeta_db('series_genre')

            try:
                infoproperties['set.genres'] = ' / '.join(tuple((i['name'] for i in data_list.cached_data)))
            except IndexError:
                pass

            if not self.parent_db_cache.extendedinfo:
                return infoproperties

            data_list = self.return_basemeta_db('series_movie')

            try:
                for x, i in enumerate(data_list.cached_data, 1):
                    for k in data_list.keys:
                        infoproperties[f'set.{x}.{k}'] = i[k]
            except IndexError:
                pass

        return infoproperties


class Series(BaseItem):
    get_unique_ids = MediaItem.get_unique_ids

    art_dbclist_routes = (
        (('art_poster', None), 'poster'),
        (('art_fanart', None), 'fanart'),
    )

    infoproperties_dbclist_routes = ()

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbclist_routes,
            (('series_genre', None), 'name', 'genre'),
        )

    @property
    def infolabels_dbcitem_routes(self):
        return (
            *super().infolabels_dbcitem_routes,
            (('series_stats', None), 'rating', 'rating'),
            (('series_stats', None), 'votes', 'votes'),
            (('series_stats', None), 'year_first', 'year'),
        )

    @property
    def collection_id(self):
        return self.parent_db_cache.parent_id

    def return_basemeta_db(self, *args, **kwargs):
        return_basemeta_db = super().return_basemeta_db(*args, **kwargs)
        return_basemeta_db.collection_id = self.collection_id
        return return_basemeta_db

    def get_infoproperties_special(self, infoproperties):
        infoproperties['tmdb_type'] = 'collection'
        infoproperties = SeriesItem.get_infoproperties_collection(self, infoproperties)
        return infoproperties
