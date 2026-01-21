from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem, MediaItemArtworkRoutes
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes, MediaItemInfoPropertyItemRoutes


class Season(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.imdbnumber,
        MediaItemInfoLabelItemRoutes.english_plot,
    )

    @property
    def art_dbclist_routes(self):
        return (
            MediaItemArtworkRoutes().configured_routes
            + MediaItemArtworkRoutes('tvshow').configured_routes
        )

    infoproperties_dbcitem_routes = (
        MediaItemInfoPropertyItemRoutes.watchedcount,
    )

    infoproperties_dbclist_routes = (
        *MediaItem.infoproperties_dbclist_routes,
        {
            'instance': ('network', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'icon': 'logo', 'country': 'country'},
            'propname': ('network', ),
            'joinings': None
        }
    )

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbclist_routes,
            MediaItemInfoLabelItemRoutes.network,
        )

    def get_infolabels_details(self):
        infolabels = super().get_infolabels_details()
        return infolabels

    def get_infoproperties_custom(self, infoproperties):
        infoproperties = super().get_infoproperties_custom(infoproperties)
        infoproperties = super().get_infoproperties_custom(infoproperties, 'tvshow')
        return infoproperties

    def get_infoproperties_translation(self, infoproperties):
        infoproperties = super().get_infoproperties_translation(infoproperties)
        infoproperties = super().get_infoproperties_translation(infoproperties, 'tvshow')
        return infoproperties

    def get_unique_ids(self, unique_ids):
        unique_ids = super().get_unique_ids(unique_ids)
        unique_ids = super().get_unique_ids(unique_ids, 'tvshow')
        return unique_ids

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        infoproperties = self.get_infoproperties_translation(infoproperties)
        try:
            infoproperties['totalepisodes'] = self.get_data_value('totalepisodes')
            infoproperties['airedepisodes'] = self.get_data_value('airedepisodes')
        except (TypeError, KeyError, IndexError):
            pass
        infoproperties = self.get_infoproperties_next_ep(infoproperties)
        return infoproperties
