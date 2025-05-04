from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class ImageMediaList(FanartMediaList):
    @property
    def cached_data_values(self):
        return (self.item_id, 'profiles')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)


class Person(ImageMediaList):
    pass
