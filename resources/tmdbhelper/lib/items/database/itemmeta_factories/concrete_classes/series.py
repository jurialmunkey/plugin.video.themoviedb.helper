from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem


class SeriesItem:
    def get_infoproperties_collection(self, infoproperties, collection_id):

        if collection_id:

            data_list = self.parent_db_cache.get_cached_list_values(
                keys=(
                    'ROUND(AVG(rating), 1) as rating',
                    'SUM(votes) as votes',
                    'COUNT(movie.tmdb_id) as numitems',
                    'MAX(year) as year_last',
                    'MIN(year) as year_first',
                ),
                table='movie INNER JOIN belongs ON belongs.id = movie.id',
                conditions='belongs.parent_id=? GROUP BY belongs.parent_id',
                values=(collection_id,),
            )

            try:
                infoproperties['set.rating'] = data_list[0]['rating']
                infoproperties['set.votes'] = data_list[0]['votes']
                infoproperties['set.numitems'] = data_list[0]['numitems']
                infoproperties['set.year.last'] = data_list[0]['year_last']
                infoproperties['set.year.first'] = data_list[0]['year_first']
                infoproperties['set.years'] = f"{data_list[0]['year_first']} - {data_list[0]['year_last']}"
            except IndexError:
                pass

            data_list = self.parent_db_cache.get_cached_list_values(
                keys=('DISTINCT name',),
                table='genre INNER JOIN belongs ON genre.parent_id = belongs.id',
                conditions='belongs.parent_id=? ORDER BY name',
                values=(collection_id,),
            )

            try:
                infoproperties['set.genres'] = ' / '.join(tuple((i['name'] for i in data_list)))
            except IndexError:
                pass

            if not self.parent_db_cache.extendedinfo:
                return infoproperties

            data_keys = (
                'title', 'year', 'plot', 'duration', 'premiered', 'status',
                'rating', 'votes', 'popularity', 'tmdb_id', 'originaltitle',
            )
            data_list = self.parent_db_cache.get_cached_list_values(
                keys=data_keys,
                table='movie INNER JOIN belongs ON belongs.id = movie.id',
                conditions='belongs.parent_id=? ORDER BY year',
                values=(collection_id,),)

            try:
                for x, i in enumerate(data_list, 1):
                    for k in data_keys:
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

    def get_infoproperties_special(self, infoproperties):
        infoproperties['tmdb_type'] = 'collection'
        infoproperties = SeriesItem.get_infoproperties_collection(self, infoproperties, self.parent_db_cache.item_id)
        return infoproperties
