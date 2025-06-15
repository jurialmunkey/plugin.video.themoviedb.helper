
from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList, ArtworkDetailsMixin


class Art(ItemDetailsList):
    table = 'art'
    keys = ('aspect_ratio', 'quality', 'iso_language', 'icon', 'type', 'extension', 'rating', 'votes', 'parent_id',)
    conditions = 'parent_id=? ORDER BY rating DESC'  # WHERE conditions
    conflict_constraint = 'icon, type, parent_id'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class ArtType(ArtworkDetailsMixin, Art):
    conditions = 'parent_id=? AND type=? ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_fanart(v)


class ArtPoster(ArtType):
    conditions = 'parent_id=? AND type=? ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'posters')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)


class ArtProfile(ArtType):
    conditions = 'parent_id=? AND type=? ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'profiles')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_poster(v)

    def get_cached_data(self):
        return self.get_cached_data_by_null()


class ArtPosterLanguage(ArtPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class ArtPosterEnglish(ArtPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class ArtPosterNull(ArtPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_null()


class ArtThumbs(ArtType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'stills')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_thumbs(v)

    def get_cached_data(self):
        return self.get_cached_data_by_null()


class ArtFanart(ArtType):
    conditions = 'parent_id=? AND type=? ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'backdrops', )

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_fanart(v)

    def get_cached_data(self):
        return self.get_cached_data_by_null()


class ArtExtraFanart(ArtFanart):
    conditions = 'parent_id=? AND type=? ORDER BY rating DESC LIMIT 10 OFFSET 1'  # WHERE conditions


class ArtLandscape(ArtFanart):
    conditions = 'parent_id=? AND (type=? OR type=?) ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'backdrops', 'stills')

    def get_cached_data(self):
        return self.get_cached_data_by_language() or self.get_cached_data_by_english()


class ArtLandscapeLanguage(ArtLandscape):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class ArtLandscapeEnglish(ArtLandscape):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class ArtClearlogo(ArtType):
    conditions = 'parent_id=? AND type=? AND extension=? ORDER BY rating DESC LIMIT 1'  # WHERE conditions

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'logos', 'png')

    def image_path_func(self, v):
        return self.common_apis.tmdb_imagepath.get_imagepath_clogos(v)


class ArtClearlogoLanguage(ArtClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class ArtClearlogoEnglish(ArtClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class ArtClearlogoNull(ArtClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_english()
