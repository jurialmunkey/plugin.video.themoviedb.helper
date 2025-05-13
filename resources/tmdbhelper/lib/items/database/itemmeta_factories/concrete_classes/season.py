from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem, MediaItemArtworkRoutes, MediaItemInfoLabelItemRoutes
from tmdbhelper.lib.addon.plugin import get_setting


class SeasonItemArtworkRoutes:
    art_dbclist_routes_fanart_tv = (
        (('fanart_tv_poster', 'tvshow'), 'poster'),
        (('fanart_tv_fanart', 'tvshow'), 'fanart'),
        (('fanart_tv_landscape', 'tvshow'), 'landscape'),
        (('fanart_tv_clearlogo', 'tvshow'), 'clearlogo'),
        (('fanart_tv_clearart', 'tvshow'), 'clearart'),
        (('fanart_tv_banner', 'tvshow'), 'banner'),
    )

    art_dbclist_routes_tmdb = (
        (('art_poster', 'tvshow'), 'poster'),
        (('art_fanart', 'tvshow'), 'fanart'),
        (('art_landscape', 'tvshow'), 'landscape'),
        (('art_clearlogo', 'tvshow'), 'clearlogo'),
        (('art_extrafanart', 'tvshow'), 'fanart'),
    )


class Season(MediaItem):
    infolabels_dbcitem_routes = (
        MediaItemInfoLabelItemRoutes.certification,
        (('video', None), 'path', 'trailer'),
        (('watchedcount', None), 'watched_episodes', 'playcount'),
    )

    @property
    def art_dbclist_routes(self):
        return (
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
            *SeasonItemArtworkRoutes.art_dbclist_routes_tmdb,
        ) if not get_setting('fanarttv_lookup') else (
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
            *MediaItemArtworkRoutes.art_dbclist_routes_fanart_tv,
            *SeasonItemArtworkRoutes.art_dbclist_routes_tmdb,
            *SeasonItemArtworkRoutes.art_dbclist_routes_fanart_tv,
        ) if not get_setting('fanarttv_prefer') else (
            *MediaItemArtworkRoutes.art_dbclist_routes_fanart_tv,
            *MediaItemArtworkRoutes.art_dbclist_routes_tmdb,
            *SeasonItemArtworkRoutes.art_dbclist_routes_fanart_tv,
            *SeasonItemArtworkRoutes.art_dbclist_routes_tmdb,
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

    def get_infolabels_details(self):
        infolabels = super().get_infolabels_details()
        infolabels['episode'] = self.get_data_value('totalepisodes')
        return infolabels

    def get_infoproperties_custom(self, infoproperties):
        infoproperties = super().get_infoproperties_custom(infoproperties)
        for i in self.parent_db_cache.return_basemeta_db('custom', 'tvshow').cached_data:
            infoproperties[f"tvshow.{i['key']}"] = i['value']
        return infoproperties

    def get_unique_ids(self, unique_ids):
        unique_ids = super().get_unique_ids(unique_ids)
        for i in self.parent_db_cache.return_basemeta_db('unique_id', 'tvshow').cached_data:
            unique_ids[f"tvshow.{i['key']}"] = i['value']
        unique_ids['tmdb'] = unique_ids['tvshow.tmdb'] = self.parent_db_cache.tmdb_id
        return unique_ids

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        try:
            infoproperties['totalepisodes'] = infoproperties['unwatchedepisodes'] = self.get_data_value('totalepisodes')
        except (TypeError, KeyError, IndexError):
            pass
        return infoproperties
