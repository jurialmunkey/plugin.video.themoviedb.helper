from tmdbhelper.lib.script.sync.trakt.item import ItemSync
from tmdbhelper.lib.script.sync.actions import (
    ItemWatched as BasicItemWatched,
    ItemUnwatched as BasicItemUnwatched,
    ItemWatchlist as BasicItemWatchlist,
    ItemCollection as BasicItemCollection,
    ItemDropped as BasicItemDropped,
)


class ItemWatched(ItemSync, BasicItemWatched):
    sync_url = 'history'


class ItemUnwatched(ItemSync, BasicItemUnwatched):
    sync_url = 'history'


class ItemWatchlist(ItemSync, BasicItemWatchlist):
    sync_url = 'watchlist'

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.syncdata.cache.del_item(table='lactivities', item_id='show.watchlist')
        self.syncdata.cache.del_item(table='lactivities', item_id='movie.watchlist')
        self.syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemCollection(ItemSync, BasicItemCollection):
    sync_url = 'collection'

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.syncdata.cache.del_item(table='lactivities', item_id='show.collection')
        self.syncdata.cache.del_item(table='lactivities', item_id='movie.collection')
        self.syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemFavorites(ItemSync):
    localized_name_add = 32490
    localized_name_rem = 32491
    sync_key = 'favorites_listed_at'
    sync_url = 'favorites'

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.syncdata.cache.del_item(table='lactivities', item_id='show.favorites')
        self.syncdata.cache.del_item(table='lactivities', item_id='movie.favorites')
        self.syncdata.reset_lastactivities()
        self.get_sync_value()


class ItemDropped(ItemSync, BasicItemDropped):
    sync_url = 'hidden/dropped'

    def get_post_response_args(self):
        return ('users', self.method, )

    def reset_lastactivities(self):
        if not self.is_successful_sync:
            return
        self.syncdata.cache.del_item(table='lactivities', item_id='show.nextup')  # Resync data after dropping a show
        self.syncdata.cache.del_item(table='lactivities', item_id='show.watched')  # Resync data after dropping a show
        self.syncdata.reset_lastactivities()
        self.delete_listdata()  # We also reset cached lists as calendars might drop shows
