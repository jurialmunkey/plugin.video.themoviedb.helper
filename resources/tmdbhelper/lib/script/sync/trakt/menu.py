from tmdbhelper.lib.script.sync.trakt.basic import (
    ItemWatched,
    ItemUnwatched,
    ItemWatchlist,
    ItemCollection,
    ItemFavorites,
    ItemDropped
)
from tmdbhelper.lib.script.sync.trakt.rating import ItemRating
from tmdbhelper.lib.script.sync.trakt.comments import ItemComments
from tmdbhelper.lib.script.sync.trakt.userlist import (
    ItemUserList,
    ItemMDbList
)
from tmdbhelper.lib.script.sync.trakt.progress import ItemProgress
from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu


class Menu(BasicMenu):
    items = {
        'watched': ItemWatched,
        'unwatched': ItemUnwatched,
        'watchlist': ItemWatchlist,
        'collection': ItemCollection,
        'favorites': ItemFavorites,
        'userlist': ItemUserList,
        'mdblistuser': ItemMDbList,
        'progress': ItemProgress,
        'comments': ItemComments,
        'dropped': ItemDropped,
        'rating': ItemRating,
    }


def sync_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    menu = Menu(tmdb_type, tmdb_id, season, episode)
    menu.select(sync_type)
