from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu
from tmdbhelper.lib.script.sync.tmdb.basic import (
    ItemWatchlist,
    ItemFavorite,
)
from tmdbhelper.lib.script.sync.tmdb.userlist import ItemUserList
from tmdbhelper.lib.script.sync.tmdb.rating import ItemRating


class Menu(BasicMenu):
    items = {
        'watchlist': ItemWatchlist,
        'favorite': ItemFavorite,
        'userlist': ItemUserList,
        'rating': ItemRating,
    }


def sync_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    from tmdbhelper.lib.api.tmdb.users import TMDbUser
    if not TMDbUser().authenticator.authorised_access:
        return
    menu = Menu(tmdb_type, tmdb_id, season, episode)
    menu.select(sync_type)
