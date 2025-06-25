from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MIN, SQLITE_TRUE
from tmdbhelper.lib.addon.plugin import get_localized


class FTVFanartMediaList(FanartMediaList):
    table = 'fanart_tv'
    cached_data_base_conditions = 'parent_id=? AND type=? AND baseitem.expiry>=? AND baseitem.datalevel>=? AND baseitem.fanart_tv>=?'
    cached_data_table = 'baseitem INNER JOIN fanart_tv ON fanart_tv.parent_id = baseitem.id'
    cached_data_value_type = 'fanart'
    keys = ('icon', 'iso_language', 'likes', 'parent_id')

    sort_by_fallback = 'likes'
    order_by_direction_fallback = 'DESC'

    filter_key_map = {
        'iso_language': 'iso_language',
        'likes': 'likes',
        'quality': 'quality',
        'type': 'type',
        'extension': 'extension',
    }

    @property
    def cached_data_values(self):
        return (self.item_id, self.cached_data_value_type, self.current_time, DATALEVEL_MIN, SQLITE_TRUE)

    def image_path_func(self, v):
        return v

    @staticmethod
    def map_label2(i):
        return ' | '.join((
            f"{get_localized(248)}={i['iso_language']}",
            f"{get_localized(32128)}={i['likes']}",
        ))


class Movie(FTVFanartMediaList):
    pass


class Tvshow(FTVFanartMediaList):
    pass


class Season(FTVFanartMediaList):
    pass


class Episode(FTVFanartMediaList):
    pass
