from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ftv_fanart import FTVFanartMediaList


class FTVLandscapeMediaList(FTVFanartMediaList):
    cached_data_value_type = 'landscape'


class Movie(FTVLandscapeMediaList):
    pass


class Tvshow(FTVLandscapeMediaList):
    pass


class Season(FTVLandscapeMediaList):
    pass


class Episode(FTVLandscapeMediaList):
    pass
