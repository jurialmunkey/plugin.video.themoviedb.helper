from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class PosterMediaList(FanartMediaList):
    @property
    def cached_data_values(self):
        return (self.item_id, 'posters')

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
