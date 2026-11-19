from random import shuffle
from urllib.parse import unquote
from xbmc import Monitor
from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import BusyDialog
from tmdbhelper.lib.addon.plugin import executebuiltin, get_localized
from tmdbhelper.lib.items.context_random import PlayRandomContextMenu, PlayRandomPath
from tmdbhelper.lib.items.router import Router


class PlayRandom:
    """Try shuffled branches on each page until one yields a playable item."""

    def __init__(self, path):
        self.folder = PlayRandomPath(path)
        self.visited = set()

    @cached_property
    def monitor(self):
        return self.get_monitor()

    @staticmethod
    def get_monitor():
        return Monitor()

    def get_items(self, folder):
        items = Router(-1, folder.paramstring).get_directory(items_only=True) or []
        items = [PlayRandomContextMenu(item) for item in items if item]
        items = [item for item in items if item.is_folder or item.is_playable]
        shuffle(items)
        return iter(items)

    def get_branch(self, folder):
        if self.monitor.abortRequested() or folder.paramstring in self.visited:
            return iter(())
        self.visited.add(folder.paramstring)
        return self.get_items(folder)

    @cached_property
    def item(self):
        return self.get_item()

    def get_item(self):
        if not self.folder.is_folder:
            return
        # An explicit stack also handles deeply nested custom folders.
        branches = [self.get_branch(self.folder)]
        while branches and not self.monitor.abortRequested():
            try:
                item = next(branches[-1])
            except StopIteration:
                branches.pop()
                continue
            if item.is_playable:
                return item.listitem
            branches.append(self.get_branch(item.folder))

    def play(self):
        with BusyDialog():
            item = self.item
        if self.monitor.abortRequested():
            return
        if item is None:
            return Dialog().notification(get_localized(32767), get_localized(32769))
        executebuiltin(f'PlayMedia("{item.url}",playlist_type_hint=1)')


def play_random(play_random, **kwargs):
    return PlayRandom(unquote(play_random)).play()
