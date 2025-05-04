from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.basemedia import MediaList


class FanartMediaList(MediaList):
    cached_data_table = table = 'art'
    cached_data_conditions_base = 'parent_id=? AND type=? ORDER BY rating DESC'
    cached_data_check_key = 'parent_id'
    keys = ('icon', 'iso_language', 'rating', 'parent_id')
    item_mediatype = 'image'
    item_tmdb_type = 'image'
    item_label_key = 'icon'
    item_alter_key = ''

    @property
    def cached_data_values(self):
        return (self.item_id, 'backdrops')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_fanart(v)

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
