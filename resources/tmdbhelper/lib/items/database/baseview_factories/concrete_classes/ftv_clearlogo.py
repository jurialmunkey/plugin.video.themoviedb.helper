from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ftv_fanart import FTVFanartMediaList


class FTVClearlogoMediaList(FTVFanartMediaList):
    cached_data_value_type = 'clearlogo'


class Movie(FTVClearlogoMediaList):
    pass


class Tvshow(FTVClearlogoMediaList):
    pass


class Season(FTVClearlogoMediaList):
    pass


class Episode(FTVClearlogoMediaList):
    pass
