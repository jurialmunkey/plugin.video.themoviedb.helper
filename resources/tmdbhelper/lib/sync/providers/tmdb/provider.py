from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper.lib.sync.providers.tmdb.ratings import TMDbRatingsSupplier


class Provider(SyncProvider):
    interface_version = 3
    provider_id = 'tmdb'
    display_name = 'TMDb'
    addon_id = 'plugin.video.themoviedb.helper'
    ratings_classes = {
        'movie': TMDbRatingsSupplier,
        'tvshow': TMDbRatingsSupplier,
    }

    @cached_property
    def api(self):
        return self.get_api()

    def get_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    def is_authorized(self):
        return True
