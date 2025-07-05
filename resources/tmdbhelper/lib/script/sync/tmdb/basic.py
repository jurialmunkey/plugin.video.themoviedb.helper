from tmdbhelper.lib.script.sync.tmdb.item import ItemSync


class ItemWatchlist(ItemSync):
    localized_name_add = 32291
    localized_name_rem = 32292
    tmdb_list_type = 'watchlist'


class ItemFavorite(ItemSync):
    localized_name_add = 32490
    localized_name_rem = 32491
    tmdb_list_type = 'favorite'
