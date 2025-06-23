from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList


class ClearlogoMediaList(FanartMediaList):
    cached_data_value_type = 'logos'
    cached_data_base_conditions = 'parent_id=? AND type=? AND extension=\'png\' AND baseitem.expiry>=? AND baseitem.datalevel>=?'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_clogos(v)


class Movie(ClearlogoMediaList):
    pass


class Tvshow(ClearlogoMediaList):
    pass


class Season(ClearlogoMediaList):
    pass


class Episode(ClearlogoMediaList):
    pass
