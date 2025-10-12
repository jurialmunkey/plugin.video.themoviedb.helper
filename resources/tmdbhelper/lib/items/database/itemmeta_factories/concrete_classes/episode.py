from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem, MediaItemArtworkRoutes
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseroutes import MediaItemInfoLabelItemRoutes
from tmdbhelper.lib.items.database.mappings import ItemMapperMethods
from tmdbhelper.lib.addon.tmdate import is_future_timestamp


class Episode(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        MediaItemInfoLabelItemRoutes.trailer,
        MediaItemInfoLabelItemRoutes.playcount,
    )

    @property
    def art_dbclist_routes(self):
        return (
            MediaItemArtworkRoutes().configured_routes
            + MediaItemArtworkRoutes('season').configured_routes
            + MediaItemArtworkRoutes('tvshow').configured_routes
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
            (('network', None), 'name', 'studio'),
        )

    def get_premiered_status(self):
        premiered = self.get_data_value('premiered')
        if not premiered:
            return 'Unknown'
        if is_future_timestamp(premiered, "%Y-%m-%d", 10, use_today=True, days=1):
            return 'Anticipated'
        if is_future_timestamp(premiered, "%Y-%m-%d", 10, use_today=True, days=0):
            return 'Airing'
        return 'Released'

    def get_unique_ids(self, unique_ids):
        unique_ids = super().get_unique_ids(unique_ids)
        unique_ids = super().get_unique_ids(unique_ids, 'season')
        unique_ids = super().get_unique_ids(unique_ids, 'tvshow')
        return unique_ids

    def get_infoproperties_custom(self, infoproperties):
        infoproperties = super().get_infoproperties_custom(infoproperties)
        infoproperties = super().get_infoproperties_custom(infoproperties, 'tvshow')
        infoproperties = super().get_infoproperties_custom(infoproperties, 'season')
        return infoproperties

    def get_infoproperties_translation(self, infoproperties):
        infoproperties = super().get_infoproperties_translation(infoproperties)
        infoproperties = super().get_infoproperties_translation(infoproperties, 'tvshow')
        infoproperties = super().get_infoproperties_translation(infoproperties, 'season')
        return infoproperties

    def get_infoproperties_episode_type(self, infoproperties):
        infoproperties['episode_type'] = self.get_data_value('episode_type')
        infoproperties['episode_status'] = self.get_premiered_status()
        return infoproperties

    def get_infoproperties_tvshow(self, infoproperties):
        infoproperties['tvshow.originaltitle'] = self.get_data_value('tvshow_originaltitle')
        infoproperties['tvshow.year'] = self.get_data_value('tvshow_year')
        infoproperties.update(ItemMapperMethods.get_custom_date(
            self.get_data_value('tvshow_premiered'), name='tvshow.premiered'
        ))
        return infoproperties

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        infoproperties = self.get_infoproperties_translation(infoproperties)
        infoproperties = self.get_infoproperties_episode_type(infoproperties)
        infoproperties = self.get_infoproperties_lastplayed(infoproperties)
        infoproperties = self.get_infoproperties_progress(infoproperties)
        infoproperties = self.get_infoproperties_tvshow(infoproperties)
        infoproperties = self.get_infoproperties_next_ep(infoproperties)
        return infoproperties
