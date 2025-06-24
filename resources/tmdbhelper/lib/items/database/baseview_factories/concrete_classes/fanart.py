from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList
from tmdbhelper.lib.addon.consts import DATALEVEL_MIN
from tmdbhelper.lib.addon.plugin import get_localized


class FanartMediaList(MediaList):
    table = 'art'
    cached_data_table = 'baseitem INNER JOIN art ON art.parent_id = baseitem.id'
    cached_data_base_conditions = 'parent_id=? AND type=? AND baseitem.expiry>=? AND baseitem.datalevel>=?'
    cached_data_value_type = 'backdrops'
    cached_data_check_key = 'parent_id'
    keys = ('icon', 'iso_language', 'rating', 'votes', 'parent_id')
    item_mediatype = 'image'
    item_tmdb_type = 'image'
    item_label_key = 'icon'
    item_alter_key = ''

    sort_by_fallback = 'rating'
    order_by_direction_fallback = 'DESC'

    filter_key_map = {
        'iso_language': 'iso_language',
        'rating': 'rating',
        'votes': 'votes',
        'aspect_ratio': 'aspect_ratio',
        'quality': 'quality',
        'type': 'type',
        'extension': 'extension',
    }

    sort_direction = {
        'appearances': 'DESC',
    }

    @property
    def cached_data_values(self):
        return (self.item_id, self.cached_data_value_type, self.current_time, DATALEVEL_MIN)

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_fanart(v)

    @staticmethod
    def map_label2(i):
        return ' | '.join((
            f"{get_localized(248)}={i['iso_language']}",
            f"{get_localized(563)}={i['rating']}",
            f"{get_localized(205)}={i['votes']}",
        ))

    @staticmethod
    def map_item_unique_ids(i):
        return {}

    @staticmethod
    def map_item_params(i):
        return {}

    def map_item_art(self, i):
        return {
            'thumb': self.image_path_func(i['icon'])
        }

    def map_item(self, i):  # TODO: Need to figure out how to set as slideshow (maybe needs new ListItem class type)
        item = super().map_item(i)
        item['path'] = item['art']['thumb']
        item['is_folder'] = True
        return item


class Movie(FanartMediaList):
    pass


class Tvshow(FanartMediaList):
    pass


class Season(FanartMediaList):
    pass


class Episode(FanartMediaList):
    pass
