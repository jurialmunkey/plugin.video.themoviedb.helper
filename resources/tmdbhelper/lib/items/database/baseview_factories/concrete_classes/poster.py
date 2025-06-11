from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class PosterMediaList(FanartMediaList):
    cached_data_value_type = 'posters'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)


class Movie(PosterMediaList):
    pass


class Tvshow(PosterMediaList):
    pass


class Season(PosterMediaList):
    pass


class Episode(PosterMediaList):
    pass
