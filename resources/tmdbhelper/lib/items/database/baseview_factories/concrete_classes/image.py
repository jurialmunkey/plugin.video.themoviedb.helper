from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class ImageMediaList(FanartMediaList):
    cached_data_value_type = 'profiles'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)


class Person(ImageMediaList):
    pass
