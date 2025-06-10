from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class ThumbMediaList(FanartMediaList):
    cached_data_value_type = 'stills'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Episode(ThumbMediaList):
    pass
