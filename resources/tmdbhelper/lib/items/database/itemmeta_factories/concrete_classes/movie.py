from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.series import SeriesItem


class Movie(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.playcount,
    )

    @property
    def collection_id(self):
        return self.get_data_value('collection_id')

    def return_basemeta_db(self, *args, **kwargs):
        return_basemeta_db = super().return_basemeta_db(*args, **kwargs)
        return_basemeta_db.collection_id = self.collection_id
        return return_basemeta_db

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
        infoproperties = self.get_infoproperties_translation(infoproperties)
        infoproperties = self.get_infoproperties_progress(infoproperties)
        infoproperties = self.get_infoproperties_lastplayed(infoproperties)
        infoproperties = self.get_infoproperties_ranks(infoproperties)
        infoproperties = self.get_infoproperties_collection(infoproperties)
        return infoproperties

    def get_infoproperties_collection(self, infoproperties):
        if self.collection_id:

            try:
                from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
                tmdb_imagepath = TMDbImagePath()
                infoproperties['set.title'] = infoproperties['set.name'] = self.data[0]['collection_title']
                infoproperties['set.tmdb_id'] = self.data[0]['collection_tmdb_id']
                infoproperties['set.poster'] = tmdb_imagepath.get_imagepath_poster(self.data[0]['collection_poster'])
                infoproperties['set.fanart'] = tmdb_imagepath.get_imagepath_fanart(self.data[0]['collection_fanart'])
            except (TypeError, KeyError, IndexError):
                pass

            infoproperties = SeriesItem.get_infoproperties_collection(self, infoproperties)

        return infoproperties
