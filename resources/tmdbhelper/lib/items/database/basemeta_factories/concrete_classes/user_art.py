from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class UserArt(ItemDetailsList):
    table = 'user_art'
    keys = ('icon', 'type', 'parent_id',)
    conditions = 'parent_id=? AND type=? LIMIT 1'  # WHERE conditions
    conflict_constraint = 'icon, parent_id'
    artwork_type = None

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.artwork_type, )

    def image_path_func(self, v):
        return v


class UserArtPoster(UserArt):
    artwork_type = 'poster'


class UserArtFanart(UserArt):
    artwork_type = 'fanart'


class UserArtLandscape(UserArt):
    artwork_type = 'landscape'


class UserArtClearlogo(UserArt):
    artwork_type = 'clearlogo'
