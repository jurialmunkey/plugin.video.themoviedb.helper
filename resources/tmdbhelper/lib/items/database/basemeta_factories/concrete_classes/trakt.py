from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.baseclass import ItemDetailsList


class SimpleCache(ItemDetailsList):
    table = 'simplecache'
    conditions = 'id=? LIMIT 1'

    @property
    def values(self):  # WHERE conditions values for ?
        return (self.item_id, )


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
