from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class SimpleCache(ItemDetailsList):
    """Read item metadata cached by the configured sync providers."""
    table = 'simplecache'
    conditions = 'id=? LIMIT 1'
    sync_details = True  # Set False to read the item as if it had never been synced

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )

    def get_cached_data(self):
        if not self.sync_details:
            return []
        return super().get_cached_data()


class PlayCount(SimpleCache):
    keys = ('plays', )


class WatchedCount(SimpleCache):
    keys = ('watched_episodes', )


class AiredCount(SimpleCache):
    keys = ('aired_episodes', )


class PlayProgress(SimpleCache):
    keys = ('playback_progress', )


class FavoritesRank(SimpleCache):
    keys = ('favorites_rank', )


class WatchlistRank(SimpleCache):
    keys = ('watchlist_rank', )


class CollectedDate(SimpleCache):
    keys = ('collection_last_collected_at', )


class LastPlayed(SimpleCache):
    keys = ('last_watched_at', 'playback_paused_at')
    cached_data_keys = ('MAX(ifnull(last_watched_at, ""), ifnull(playback_paused_at, "")) as lastplayed', )
