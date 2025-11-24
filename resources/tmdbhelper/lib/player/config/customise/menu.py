from xbmcgui import Dialog
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.addon.dialog import busy_decorator
from tmdbhelper.lib.player.config.files import PlayerFiles
from tmdbhelper.lib.player.config.customise.item import PlayerCustomiseDialogItem
from jurialmunkey.ftools import cached_property


class PlayerCustomiseDialogMenuMain:

    @cached_property
    def players(self):
        return self.get_players()

    def get_players(self):
        players = {}
        players.update(self.players_other)
        players.update(self.players_files)
        return players

    players_other = {
        'create_player': {
            'name': get_localized(32140),
            'icon': '-',
            'priority': 1
        }
    }

    @cached_property
    def players_files(self):
        return PlayerFiles(show_disabled=True).dictionary

    @cached_property
    def players_prioritised(self):
        return sorted((
            PlayerCustomiseDialogItem(filename, metadata)
            for filename, metadata in self.players.items()
        ), key=lambda i: i.priority)

    @cached_property
    def dialog_options(self):
        return self.get_dialog_options()

    @busy_decorator
    def get_dialog_options(self):
        return [i.listitem for i in self.players_prioritised]

    @cached_property
    def choice(self):
        x = Dialog().select(get_localized(32328), self.dialog_options, useDetails=True)
        return self.players_prioritised[x] if x != -1 else None

    def select(self):
        if not self.choice:
            return
        self.choice.configure()
        return self.choice


class PlayerCustomiseDialogMenuFallbacks(PlayerCustomiseDialogMenuMain):

    def __init__(self, fallback=False):
        self.fallback = fallback

    @cached_property
    def players_other(self):
        return {
            'remove_fallback': {
                'name': f'{get_localized(32141)}: {self.fallback}',
                'icon': '-',
                'priority': 1
            }
        } if self.fallback else {}


def PlayerCustomiseDialogMenu():
    while PlayerCustomiseDialogMenuMain().select():
        pass
