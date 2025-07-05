from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu
from tmdbhelper.lib.script.sync.tmdb.basic import (
    ItemWatchlist,
    ItemFavorite,
)
from tmdbhelper.lib.script.sync.tmdb.userlist import ItemUserList


class Menu(BasicMenu):
    items = {
        'watchlist': ItemWatchlist,
        'favorite': ItemFavorite,
        'userlist': ItemUserList,
    }


def sync_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    menu = Menu(tmdb_type, tmdb_id, season, episode)
    menu.select(sync_type)
