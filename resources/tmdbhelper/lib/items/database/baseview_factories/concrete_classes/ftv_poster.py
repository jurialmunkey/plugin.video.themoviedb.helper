from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ftv_fanart import FTVFanartMediaList


class FTVPosterMediaList(FTVFanartMediaList):
    cached_data_value_type = 'poster'


class Movie(FTVPosterMediaList):
    pass


class Tvshow(FTVPosterMediaList):
    pass


class Season(FTVPosterMediaList):
    pass


class Episode(FTVPosterMediaList):
    pass
