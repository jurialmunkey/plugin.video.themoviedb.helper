from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.fanart import FanartMediaList
from jurialmunkey.ftools import cached_property


class ThumbMediaList(FanartMediaList):
    cached_data_value_type = 'stills'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)


class Episode(ThumbMediaList):
    @cached_property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)
