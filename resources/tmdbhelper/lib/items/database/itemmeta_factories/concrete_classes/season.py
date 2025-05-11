from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem


class Season(MediaItem):
    infolabels_dbcitem_routes = (
        (('certification', None), 'name', 'mpaa'),
        (('video', None), 'path', 'trailer'),
    )

    art_dbclist_routes = (
        *MediaItem.art_dbclist_routes,
        (('art_poster', 'tvshow'), 'poster'),
        (('art_fanart', 'tvshow'), 'fanart'),
        (('art_landscape', 'tvshow'), 'landscape'),
        (('art_clearlogo', 'tvshow'), 'clearlogo'),
        (('art_extrafanart', 'tvshow'), 'fanart'),
        (('fanart_tv_poster', 'tvshow'), 'poster'),
        (('fanart_tv_fanart', 'tvshow'), 'fanart'),
        (('fanart_tv_landscape', 'tvshow'), 'landscape'),
        (('fanart_tv_clearlogo', 'tvshow'), 'clearlogo'),
        (('fanart_tv_clearart', 'tvshow'), 'clearart'),
        (('fanart_tv_banner', 'tvshow'), 'banner'),
    )

    infoproperties_dbclist_routes = (
        *MediaItem.infoproperties_dbclist_routes,
        {
            'instance': ('studio', None),
            'mappings': {'name': 'name', 'tmdb_id': 'tmdb_id', 'logo': 'logo', 'country': 'country'},
            'propname': ('network', ),  # For backwards compatibility also set studio to network
            'joinings': None
        }
    )

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
        return infoproperties
