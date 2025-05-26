from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.baseclass import BaseItem
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.basemedia import MediaItem


class Series(BaseItem):
    get_unique_ids = MediaItem.get_unique_ids

    art_dbclist_routes = (
        (('art_poster', None), 'poster'),
        (('art_fanart', None), 'fanart'),
    )

    infoproperties_dbclist_routes = ()

    def get_infoproperties_special(self, infoproperties):
        infoproperties['tmdb_type'] = 'collection'
        return infoproperties
