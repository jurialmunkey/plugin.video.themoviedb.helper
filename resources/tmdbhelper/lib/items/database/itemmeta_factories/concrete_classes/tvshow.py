from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes, MediaItemInfoPropertyItemRoutes


class Tvshow(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.episodecount,
    )

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbclist_routes,
            (('network', None), 'name', 'studio'),
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

    def get_infolabels_details(self):
        infolabels = super().get_infolabels_details()
        infolabels['season'] = self.get_data_value('totalseasons')
        infolabels['episode'] = self.get_data_value('totalepisodes')
        return infolabels

    def get_infolabels_special(self, infolabels):
        try:
            infolabels['tvshowtitle'] = self.data[0]['title']
        except (TypeError, KeyError, IndexError):
            pass
        return infolabels

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        infoproperties = self.get_infoproperties_translation(infoproperties)
        try:
            infoproperties['totalseasons'] = self.get_data_value('totalseasons')
            infoproperties['totalepisodes'] = infoproperties['unwatchedepisodes'] = self.get_data_value('totalepisodes')
        except (TypeError, KeyError, IndexError):
            pass
        infoproperties = self.get_infoproperties_ranks(infoproperties)
        infoproperties = self.get_infoproperties_next_ep(infoproperties)
        return infoproperties
