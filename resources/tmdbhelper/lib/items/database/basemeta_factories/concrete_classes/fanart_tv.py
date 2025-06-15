from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList, ArtworkDetailsMixin


class FanartTV(ItemDetailsList):
    table = 'fanart_tv'
    keys = ('icon', 'iso_language', 'likes', 'quality', 'type', 'extension', 'parent_id',)
    conditions = 'parent_id=? ORDER BY likes DESC'  # WHERE conditions
    conflict_constraint = 'icon, type, parent_id'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


class FanartTVType(ArtworkDetailsMixin, FanartTV):
    conditions = 'parent_id=? AND type=? ORDER BY likes DESC LIMIT 1'  # WHERE conditions

    @staticmethod
    def image_path_func(v):
        return v.replace(' ', '%20')  # Ugly hack to replace unencoded spaces returned by API


class FanartTVPoster(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'posters')


class FanartTVPosterLanguage(FanartTVPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class FanartTVPosterEnglish(FanartTVPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class FanartTVPosterNull(FanartTVPoster):
    def get_cached_data(self):
        return self.get_cached_data_by_null()


class FanartTVFanart(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'fanart',)


class FanartTVLandscape(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'landscape',)


class FanartTVLandscapeLanguage(FanartTVLandscape):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class FanartTVLandscapeEnglish(FanartTVLandscape):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class FanartTVClearlogo(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'clearlogo')


class FanartTVClearlogoLanguage(FanartTVClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_language()


class FanartTVClearlogoEnglish(FanartTVClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_english()


class FanartTVClearlogoNull(FanartTVClearlogo):
    def get_cached_data(self):
        return self.get_cached_data_by_null()


class FanartTVClearart(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'clearart')


class FanartTVBanner(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'banner')


class FanartTVDiscart(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'discart')
