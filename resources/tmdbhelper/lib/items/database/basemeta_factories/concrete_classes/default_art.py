from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class DefaultArt(ItemDetailsList):
    table = 'default_art'
    keys = ('icon', 'type', 'parent_id',)
    conditions = 'parent_id=? AND type=? AND icon IS NOT NULL LIMIT 1'  # WHERE conditions
    conflict_constraint = 'type, parent_id'
    artwork_type = None

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.artwork_type, )

    def image_path_func(self, v):
        return v


class DefaultArtPoster(DefaultArt):
    artwork_type = 'posters'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)


class DefaultArtFanart(DefaultArt):
    artwork_type = 'backdrops'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_fanart(v)


class DefaultArtProfile(DefaultArt):
    artwork_type = 'profiles'

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)
