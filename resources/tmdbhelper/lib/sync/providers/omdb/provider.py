from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper.lib.sync.providers.omdb.ratings import OMDbRatingsSupplier


class Provider(SyncProvider):
    interface_version = 4
    provider_id = 'omdb'
    display_name = 'OMDb'
    addon_id = 'plugin.video.themoviedb.helper'
    ratings_classes = {
        'movie': OMDbRatingsSupplier,
        'tvshow': OMDbRatingsSupplier,
    }

    @cached_property
    def api(self):
        return self.get_api()

    def get_api(self):
        from tmdbhelper.lib.api.omdb.api import OMDb
        return OMDb()

    def is_authorized(self):
        return bool(get_setting('omdb_apikey', 'str'))
