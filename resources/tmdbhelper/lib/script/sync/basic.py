from tmdbhelper.lib.script.sync.item import ItemSync


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
