# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, KeyGetter, convert_type
from tmdbhelper.lib.files.futils import get_json_filecache, set_json_filecache
from tmdbhelper.lib.addon.consts import PLAYERS_CHOSEN_DEFAULTS_FILENAME


"""
Getters
"""


class PlayerDefaultUserChoiceGetter:
    def __init__(self, tmdb_type, tmdb_id, **kwargs):
        self.tmdb_type = tmdb_type
        self.tmdb_id = f'{tmdb_id}' if tmdb_id else None

    @cached_property
    def meta(self):
        return get_json_filecache(PLAYERS_CHOSEN_DEFAULTS_FILENAME) or {}

    @cached_property
    def file(self):
        return self.player.get('file')

    @cached_property
    def mode(self):
        return self.player.get('mode')

    @cached_property
    def info(self):
        return f'{self.file} {self.mode}' if self.file and self.mode else ''

    @cached_property
    def player(self):
        return self.get_player()

    def get_player(self):
        player = self.meta
        player = KeyGetter(player).get_key(self.tmdb_type)
        player = KeyGetter(player).get_key(self.tmdb_id)
        return player or {}


class PlayerDefaultUserChoiceGetterMovie(PlayerDefaultUserChoiceGetter):
    pass


class PlayerDefaultUserChoiceGetterTvshow(PlayerDefaultUserChoiceGetter):
    pass


class PlayerDefaultUserChoiceGetterSeason(PlayerDefaultUserChoiceGetterTvshow):
    def __init__(self, season, **kwargs):
        super().__init__(**kwargs)
        self.season = f'{season}'

    def get_player(self):
        player = super().get_player()
        player = KeyGetter(KeyGetter(player).get_key('season')).get_key(self.season) or player
        return player or {}


class PlayerDefaultUserChoiceGetterEpisode(PlayerDefaultUserChoiceGetterSeason):
    def __init__(self, episode, **kwargs):
        super().__init__(**kwargs)
        self.episode = f'{episode}'

    def get_player(self):
        player = super().get_player()
        player = KeyGetter(KeyGetter(player).get_key('episode')).get_key(self.episode) or player
        return player or {}


def PlayerDefaultUserChoiceGetterFactory(tmdb_type, tmdb_id, season=None, episode=None):
    route = {
        'movie': PlayerDefaultUserChoiceGetterMovie,
        'tvshow': PlayerDefaultUserChoiceGetterTvshow,
        'season': PlayerDefaultUserChoiceGetterSeason,
        'episode': PlayerDefaultUserChoiceGetterEpisode,
    }
    route = route[convert_type(tmdb_type, 'dbtype', season=season, episode=episode)]
    return route(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode)


"""
Setters
"""


class PlayerDefaultUserChoiceSetter:

    choice = 0

    @cached_property
    def player(self):
        from tmdbhelper.lib.player.players import PlayersFactory
        return PlayersFactory(self.tmdb_type).select_default()

    @cached_property
    def header(self):
        return self.get_header()

    def get_header(self):
        return f'{self.tmdb_type} - {self.tmdb_id}'

    @cached_property
    def message(self):
        if not self.file or not self.mode:
            return get_localized(32475).format(self.header)
        return get_localized(32474).format(f'{self.file} {self.mode}', self.header)

    def get_data(self):
        data = self.meta.setdefault(self.tmdb_type, {})
        data = data.setdefault(self.tmdb_id, {})
        return data

    def set_data(self, data):
        if self.file and self.mode:
            data.update({'file': self.file, 'mode': self.mode})
        else:
            data.clear()
        return self.meta

    @cached_property
    def data(self):
        return self.set_data(self.get_data()) if self.choice != -1 else None

    def update(self):
        if not self.player:
            return
        if not self.data:
            return
        set_json_filecache(self.data, PLAYERS_CHOSEN_DEFAULTS_FILENAME, 0)
        Dialog().ok(self.header, self.message)


class PlayerDefaultUserChoiceSetterMovie(
    PlayerDefaultUserChoiceSetter,
    PlayerDefaultUserChoiceGetterMovie
):
    pass


class PlayerDefaultUserChoiceSetterTvshow(
    PlayerDefaultUserChoiceSetter,
    PlayerDefaultUserChoiceGetterTvshow
):
    pass


class PlayerDefaultUserChoiceSetterSeason(
    PlayerDefaultUserChoiceSetterTvshow,
    PlayerDefaultUserChoiceGetterSeason
):

    @cached_property
    def options(self):
        return self.get_options()

    def get_options(self):
        return {'nolabel': get_localized(20364), 'yeslabel': get_localized(20373)}

    @cached_property
    def dialog(self):
        return Dialog().yesno

    @cached_property
    def choice(self):
        return self.dialog(self.header, get_localized(32477), **self.options)

    def get_data(self):
        data = super().get_data()
        if self.choice in (1, 2):
            data = data.setdefault('season', {})
            data = data.setdefault(f'{self.season}', {})
            self.header = f'{self.header} - S{self.season:0>2}'
        return data


class PlayerDefaultUserChoiceSetterEpisode(
    PlayerDefaultUserChoiceSetterSeason,
    PlayerDefaultUserChoiceGetterEpisode
):
    def get_options(self):
        options = super().get_options()
        options.update({'customlabel': get_localized(20359)})
        return options

    @cached_property
    def dialog(self):
        return Dialog().yesnocustom

    def get_data(self):
        data = super().get_data()
        if self.choice == 2:
            data = data.setdefault('episode', {})
            data = data.setdefault(f'{self.episode}', {})
            self.header = f'{self.header}E{self.episode:0>2}'
        return data


def PlayerDefaultUserChoiceSetterFactory(tmdb_type, tmdb_id, season=None, episode=None, **kwargs):
    route = {
        'movie': PlayerDefaultUserChoiceSetterMovie,
        'tvshow': PlayerDefaultUserChoiceSetterTvshow,
        'season': PlayerDefaultUserChoiceSetterSeason,
        'episode': PlayerDefaultUserChoiceSetterEpisode,
    }
    route = route[convert_type(tmdb_type, 'dbtype', season=season, episode=episode)]
    return route(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode)


def run(*args, **kwargs):
    return PlayerDefaultUserChoiceSetterFactory(*args, **kwargs).update()
