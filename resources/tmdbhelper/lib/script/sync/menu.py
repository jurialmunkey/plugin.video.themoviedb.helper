from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import busy_decorator


class Menu:
    items = {}

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    @cached_property
    def choices(self):
        return self.get_choices()

    @busy_decorator
    def get_choices(self):
        from tmdbhelper.lib.addon.thread import ParallelThread
        with ParallelThread([v for _, v in self.items.items()], self.item_get_self) as pt:
            item_queue = pt.queue
        return [i for i in item_queue if i]

    def item_get_self(self, i):
        return i(self.tmdb_type, self.tmdb_id, self.season, self.episode).get_self()

    def choose(self):
        if not self.choices:
            return -1
        if len(self.choices) == 1:
            return 0
        from xbmcgui import Dialog
        return Dialog().contextmenu([i.name for i in self.choices])

    def select(self, sync_type=None):
        if sync_type:
            self.items = {sync_type: self.items[sync_type]}
        x = self.choose()
        if x == -1:
            return
        self.choices[x].sync()
