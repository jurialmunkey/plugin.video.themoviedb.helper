from tmdbhelper.lib.script.sync.actions import ItemWatchlist as ProviderItemWatchlist
from tmdbhelper.lib.sync.providers.tmdb.actions.item import ItemAction


class ItemWatchlist(ItemAction, ProviderItemWatchlist):
    tmdb_list_type = 'watchlist'

    def get_sync_value(self):
        return ProviderItemWatchlist.get_sync_value(self)


class ItemFavorite(ItemAction):
    localized_name_add = 32490
    localized_name_rem = 32491
    tmdb_list_type = 'favorite'
