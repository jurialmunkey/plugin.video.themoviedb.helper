from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList, ArtworkDetailsMixin


class FanartTV(ItemDetailsList):
    table = 'fanart_tv'
    keys = ('icon', 'iso_language', 'likes', 'quality', 'type', 'extension', 'parent_id',)
    conditions = 'parent_id=? ORDER BY likes DESC'  # WHERE conditions

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


class FanartTVFanart(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'fanart',)


class FanartTVLandscape(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'landscape',)


class FanartTVClearlogo(FanartTVType):
    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, 'clearlogo')


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
