from tmdbhelper.lib.addon.consts import LASTACTIVITIES_EXPIRY
from tmdbhelper.lib.addon.tmdate import get_timestring_zulu_now
from tmdbhelper.lib.sync.datatype import DataType
from tmdbhelper.lib.sync.providers.tmdb.itemdata import TMDbWatchlistItem


class SyncWatchlist(DataType):
    keys = ('rank', 'listed_at', 'notes')
    key_prefix = 'watchlist'
    method = 'watchlist'
    last_activities_key = 'watchlisted_at'
    expiry_time = LASTACTIVITIES_EXPIRY

    def get_response_sync(self, *args, **kwargs):
        if self.item_type not in ('movie', 'show'):
            return []
        if not self.provider.is_user_authorized:
            return
        tmdb_type = 'tv' if self.item_type == 'show' else 'movie'
        return self.provider.user_lists.get_account_items(tmdb_type, 'watchlist')

    def get_first_seen(self):
        items = self.cache.get_list_values(
            keys=('id', 'watchlist_listed_at'), values=(self.item_type,),
            conditions='item_type=? AND watchlist_listed_at IS NOT NULL')
        return {item['id']: item['watchlist_listed_at'] for item in items}

    def get_syncitem(self, meta):
        item = TMDbWatchlistItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)
        item.first_seen = self.get_first_seen()
        item.synced_at = get_timestring_zulu_now()
        # Map the complete snapshot before the base pipeline clears cached columns.
        item.data
        return item
