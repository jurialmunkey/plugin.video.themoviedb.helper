from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.dialog import BusyDialog
from tmdbhelper.lib.script.sync.basic import ItemWatched, ItemUnwatched, ItemWatchlist, ItemCollection, ItemFavorites
from tmdbhelper.lib.script.sync.rating import ItemRating
from tmdbhelper.lib.script.sync.comments import ItemComments
from tmdbhelper.lib.script.sync.userlist import ItemUserList, ItemMDbList
from tmdbhelper.lib.script.sync.progress import ItemProgress
from xbmcgui import Dialog


class MenuAttributes:
    """
    choices
    """
    @cached_property
    def choices(self):
        return self.get_choices()

    def get_choices(self):
        from tmdbhelper.lib.addon.thread import ParallelThread

        def _threaditem(i):
            return i(self.tmdb_type, self.tmdb_id, self.season, self.episode).get_self()

        with BusyDialog():
            with ParallelThread([v for _, v in self.items.items()], _threaditem) as pt:
                item_queue = pt.queue
            choices = [i for i in item_queue if i]

        return choices

    """
    trakt_api
    """
    @cached_property
    def trakt_api(self):
        return self.get_trakt_api()

    def get_trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()


class Menu(MenuAttributes):
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
        'rating': ItemRating,
    }

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    def choose(self):
        if not self.choices:
            return -1
        if len(self.choices) == 1:
            return 0
        return Dialog().contextmenu([i.name for i in self.choices])

    def select(self, sync_type=None):
        if sync_type:
            self.items = {sync_type: self.items[sync_type]}
        x = self.choose()
        if x == -1:
            return
        self.choices[x].sync()


def sync_trakt_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    menu = Menu(tmdb_type, tmdb_id, season, episode)
    menu.select(sync_type)
