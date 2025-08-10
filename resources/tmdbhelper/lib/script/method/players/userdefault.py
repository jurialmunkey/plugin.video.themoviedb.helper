# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.files.futils import get_json_filecache, set_json_filecache
from tmdbhelper.lib.addon.consts import PLAYERS_CHOSEN_DEFAULTS_FILENAME
from tmdbhelper.lib.player.players import PlayersFactory


class PlayerDefaultUserChoice:

    def __init__(self, tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode

    @cached_property
    def meta(self):
        return get_json_filecache(PLAYERS_CHOSEN_DEFAULTS_FILENAME) or {}

    @cached_property
    def chosen_player(self):
        return PlayersFactory(self.tmdb_type).select_default()

    @cached_property
    def file(self):
        return self.chosen_player.get('file')

    @cached_property
    def mode(self):
        return self.chosen_player.get('mode')

    @cached_property
    def header(self):
        return f'{self.tmdb_type} - {self.tmdb_id}'

    @cached_property
    def message(self):
        if not self.file or not self.mode:
            return get_localized(32475).format(self.header)
        return get_localized(32474).format(f'{self.file} {self.mode}', self.header)

    @cached_property
    def options(self):
        options = {'nolabel': get_localized(20364), 'yeslabel': get_localized(20373)}
        options.update({'customlabel': get_localized(20359)} if self.episode is not None else {})
        return options

    @cached_property
    def dialog(self):
        if self.episode is None:
            return Dialog().yesno
        return Dialog().yesnocustom

    @cached_property
    def choice(self):
        return self.dialog(self.header, get_localized(32477), **self.options)

    @cached_property
    def data(self):

        data = self.meta.setdefault(self.tmdb_type, {})
        data = data.setdefault(self.tmdb_id, {})

        if self.season is None:
            return self.meta

        if self.choice == -1:
            return

        if self.choice in (1, 2):
            data = data.setdefault('season', {})
            data = data.setdefault(f'{self.season}', {})
            self.header = f'{self.header} - S{self.season:0>2}'

        if self.choice == 2:
            data = data.setdefault('episode', {})
            data = data.setdefault(f'{self.episode}', {})
            self.header = f'{self.header}E{self.episode:0>2}'

        if not self.file or not self.mode:
            self.meta[self.tmdb_type].pop(self.tmdb_id)

        return self.meta

    def update(self):
        if not self.data or not self.chosen_player:
            return
        set_json_filecache(self.data, PLAYERS_CHOSEN_DEFAULTS_FILENAME, 0)
        Dialog().ok(self.header, self.message)


def run(*args, **kwargs):
    return PlayerDefaultUserChoice(*args, **kwargs).update()
