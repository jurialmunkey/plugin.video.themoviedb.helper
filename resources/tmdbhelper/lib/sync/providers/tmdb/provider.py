from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.providers.base import SyncProvider
from tmdbhelper.lib.sync.providers.tmdb.ratings import TMDbRatingsSupplier
from tmdbhelper.lib.sync.providers.tmdb.watchlist import SyncWatchlist
from tmdbhelper.lib.sync.providers.tmdb.actions import ItemWatchlist, ItemFavorite, ItemRating, ItemUserList
from tmdbhelper.lib.sync.providers.tmdb.directories.routes import LIST_ROUTES


class Provider(SyncProvider):
    interface_version = 4
    provider_id = 'tmdb'
    display_name = 'TMDb'
    addon_id = 'plugin.video.themoviedb.helper'
    list_routes = LIST_ROUTES
    ratings_classes = {
        'movie': TMDbRatingsSupplier,
        'tvshow': TMDbRatingsSupplier,
    }

    @property
    def sync_classes(self):
        return {'SyncWatchlist': SyncWatchlist} if self.is_user_authorized else {}

    @property
    def action_classes(self):
        return {'watchlist': ItemWatchlist} if self.is_user_authorized else {}

    @property
    def service_action_classes(self):
        if not self.is_user_authorized:
            return {}
        return {
            'tmdbuserlist': ItemUserList,
            'tmdbrating': ItemRating,
            'tmdbfavorites': ItemFavorite,
        }

    @property
    def directory_item_class(self):
        if not self.is_user_authorized:
            return
        from tmdbhelper.lib.sync.providers.tmdb.directories.item import TMDbDirectoryItem
        return TMDbDirectoryItem

    @property
    def monitor_lists_class(self):
        if not self.is_user_authorized:
            return
        from tmdbhelper.lib.sync.providers.tmdb.monitor_lists import TMDbMonitorLists
        return TMDbMonitorLists

    @cached_property
    def user_lists(self):
        return self.get_user_lists()

    def get_user_lists(self):
        from tmdbhelper.lib.sync.providers.tmdb.lists import TMDbUserLists
        return TMDbUserLists(self)

    @property
    def is_user_authorized(self):
        # Discovery must not start the interactive authentication flow.
        from tmdbhelper.lib.api.api_keys.tmdb import USER_TOKEN
        return bool(USER_TOKEN.value)

    @cached_property
    def user_api(self):
        return self.get_user_api()

    def get_user_api(self):
        from tmdbhelper.lib.api.tmdb.users import TMDbUser
        # TMDbAPI construction also sets TMDb.api_key for future public clients.
        return TMDbUser(api_key=self.api.api_key)

    @cached_property
    def api(self):
        return self.get_api()

    def get_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    def is_authorized(self):
        return True

    def get_last_activities(self):
        # TMDb has no account activity endpoint; watchlists expire locally.
        return {}
