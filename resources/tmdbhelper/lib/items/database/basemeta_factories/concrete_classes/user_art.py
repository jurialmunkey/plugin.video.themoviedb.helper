from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList
from tmdbhelper.lib.addon.plugin import get_setting


RATINGPOSTERDB_APIKEY = get_setting('ratingposterdb_apikey', 'str')
RATINGPOSTERDB_APIURL = 'https://api.ratingposterdb.com/{api_key}/tmdb/poster-default/{content_type}-{tmdb_id}.jpg?fallback=true'


class UserArt(ItemDetailsList):
    table = 'user_art'
    keys = ('icon', 'type', 'parent_id',)
    conditions = 'parent_id=? AND type=? AND icon IS NOT NULL LIMIT 1'  # WHERE conditions
    conflict_constraint = 'icon, parent_id'
    artwork_type = None

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, self.artwork_type, )

    def image_path_func(self, v):
        return v


class UserArtPoster(UserArt):
    artwork_type = 'poster'

    def get_cached_data(self):
        cached_data = super().get_cached_data()
        cached_data = cached_data or self.get_ratingsposterdb_art()
        return cached_data

    def get_ratingsposterdb_art(self):
        if not RATINGPOSTERDB_APIKEY:
            return []
        item = self.item_id.split('.')  # tmdb_type.tmdb_id.season.episode
        if item[0] not in ('movie', 'tv'):
            return []
        return [{
            'icon': RATINGPOSTERDB_APIURL.format(
                api_key=RATINGPOSTERDB_APIKEY,
                content_type='movie' if item[0] == 'movie' else 'series',
                tmdb_id=item[1]),
            'type': 'poster',
            'parent_id': self.item_id,
        }]


class UserArtFanart(UserArt):
    artwork_type = 'fanart'


class UserArtLandscape(UserArt):
    artwork_type = 'landscape'


class UserArtClearlogo(UserArt):
    artwork_type = 'clearlogo'


class UserArtThumb(UserArt):
    artwork_type = 'thumb'
