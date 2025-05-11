from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem


class Tvshow(MediaItem):
    infolabels_dbcitem_routes = (
        (('certification', None), 'name', 'mpaa'),
        (('video', None), 'path', 'trailer'),
        (('watchedcount', None), 'watched_episodes', 'playcount'),  # TODO: FIX FOR SEASONS AS NOT SYNCED AIRED COUNT
        (('airedcount', None), 'aired_episodes', 'episode'),  # TODO: FIX FOR SEASONS AS NOT SYNCED AIRED COUNT
    )

    @property
    def infolabels_dbclist_routes(self):
        return (
            *super().infolabels_dbcitem_routes,
            (('network', None), 'name', 'studio'),
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
        infolabels['season'] = self.data[0]['totalseasons']
        infolabels['episode'] = self.data[0]['totalepisodes']
        return infolabels

    def get_infolabels_special(self, infolabels):
        try:
            infolabels['tvshowtitle'] = self.data[0]['title']
        except (TypeError, KeyError, IndexError):
            pass
        return infolabels

    def get_infoproperties_special(self, infoproperties):
        infoproperties = self.get_infoproperties_custom(infoproperties)
        try:
            infoproperties['totalseasons'] = self.data[0]['totalseasons']
            infoproperties['totalepisodes'] = infoproperties['unwatchedepisodes'] = self.data[0]['totalepisodes']
            infoproperties['next_episode_to_air_id'] = self.data[0]['next_episode_to_air_id']
        except (TypeError, KeyError, IndexError):
            pass
        return infoproperties
