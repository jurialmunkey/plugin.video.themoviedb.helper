from tmdbhelper.lib.script.sync.item import ItemSync
from jurialmunkey.parser import LazyPropertyProtected


class ItemWatched(ItemSync):
    trakt_sync_url = 'history'
    allow_seasons = True
    allow_episodes = True
    preconfigured = True
    localized_name = 16103
    remove = False


class ItemUnwatched(ItemSync):
    trakt_sync_url = 'history'
    allow_seasons = True
    allow_episodes = True
    preconfigured = True
    localized_name = 16104
    remove = True


class ItemWatchlist(ItemSync):
    localized_name_add = 32291
    localized_name_rem = 32292
    trakt_sync_key = 'watchlist_listed_at'
    trakt_sync_url = 'watchlist'


class ItemCollection(ItemSync):
    localized_name_add = 32289
    localized_name_rem = 32290
    allow_episodes = True
    trakt_sync_key = 'collection_last_collected_at'
    trakt_sync_url = 'collection'


class ItemFavorites(ItemSync):
    localized_name_add = 32490
    localized_name_rem = 32491
    trakt_sync_key = 'favorites_listed_at'
    trakt_sync_url = 'favorites'


class ItemRefresh(ItemSync):
    preconfigured = True
    localized_name = 32532
    allow_seasons = True
    allow_episodes = True

    """
    methods
    """

    choice = LazyPropertyProtected('choice')

    def get_choice(self):
        from xbmcgui import Dialog
        from tmdbhelper.lib.addon.plugin import get_localized
        choices = (
            (get_localized(19022), 'hidden_at', ('movie', 'show', )),
            (get_localized(16102), 'last_watched_at', ('movie', 'show', 'episode', )),
            (get_localized(14086), 'playback_paused_at', ('movie', 'episode', )),
            (get_localized(563), 'rated_at', ('movie', 'show', 'season', 'episode', )),
            (get_localized(1036), 'favorites_listed_at', ('movie', 'show', )),
            (get_localized(32193), 'watchlist_listed_at', ('movie', 'show', 'season', 'episode', )),
            (get_localized(32192), 'collection_last_collected_at', ('movie', 'show', 'episode', )),
        )
        x = Dialog().contextmenu([i[0] for i in choices])
        if x == -1:
            return
        return choices[x]

    def get_is_successful_sync(self):
        if not self.sync_response:
            return False
        return True

    def get_sync_response(self):
        """ Called after user selects choice """
        if not self.choice:
            return False
        from tmdbhelper.lib.api.trakt.sync.datasync import SyncData
        keys = (self.choice[1], )
        for item_type in self.choice[2]:
            SyncData(self.trakt_api).sync(item_type, keys, forced=True)
        return True

    def sync(self):
        """ Entry point """
        if not self.is_successful_sync:
            return
        self.reset_lastactivities()
        self.refresh_containers()
