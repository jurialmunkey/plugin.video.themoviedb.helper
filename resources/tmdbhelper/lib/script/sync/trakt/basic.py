from tmdbhelper.lib.script.sync.trakt.item import ItemSync


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

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='show.watchlist')
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='movie.watchlist')
        self.trakt_syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemCollection(ItemSync):
    localized_name_add = 32289
    localized_name_rem = 32290
    allow_episodes = True
    trakt_sync_key = 'collection_last_collected_at'
    trakt_sync_url = 'collection'

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='show.collection')
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='movie.collection')
        self.trakt_syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemFavorites(ItemSync):
    localized_name_add = 32490
    localized_name_rem = 32491
    trakt_sync_key = 'favorites_listed_at'
    trakt_sync_url = 'favorites'

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='show.favorites')
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='movie.favorites')
        self.trakt_syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemDropped(ItemSync):
    allow_movies = False
    allow_shows = True  # Only shows can be dropped
    allow_seasons = True  # We allow seasons and episode but convert to show
    allow_episodes = True  # We allow seasons and episode but convert to show
    localized_name_add = 32046
    localized_name_rem = 32047
    convert_episodes = True  # Convert to tvshow since we only drop shows but want access from next episodes
    convert_seasons = True  # Convert to tvshow since we only drop shows but want access from next episodes
    trakt_sync_key = 'dropped_hidden_at'
    trakt_sync_url = 'hidden/dropped'

    def get_post_response_args(self):
        return ('users', self.method, )

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='show.nextup')  # Resync data after dropping a show
        self.trakt_syncdata.cache.del_item(table='lactivities', item_id='show.watched')  # Resync data after dropping a show
        self.trakt_syncdata.reset_lastactivities()
