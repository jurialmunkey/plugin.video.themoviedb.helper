from xbmcgui import Dialog, INPUT_NUMERIC
from xbmcaddon import Addon as KodiAddon
from resources.lib.addon.plugin import ADDONPATH, get_setting, get_localized, get_condvisibility
from resources.lib.addon.parser import try_int
from resources.lib.addon.dialog import BusyDialog
from resources.lib.addon.consts import PLAYERS_BASEDIR_BUNDLED, PLAYERS_BASEDIR_USER, PLAYERS_BASEDIR_SAVE, PLAYERS_PRIORITY
from resources.lib.files.futils import get_files_in_folder
from resources.lib.files.futils import read_file, dumps_to_file, delete_file
from resources.lib.items.listitem import ListItem
from json import loads, dumps
from copy import deepcopy


def get_players_from_file():
    players = {}
    basedirs = [PLAYERS_BASEDIR_USER]
    if get_setting('bundled_players'):
        basedirs += [PLAYERS_BASEDIR_BUNDLED]
    basedirs += [PLAYERS_BASEDIR_SAVE]  # Add saved players last so they overwrite
    for basedir in basedirs:
        files = get_files_in_folder(basedir, r'.*\.json')
        for file in files:
            meta = loads(read_file(basedir + file)) or {}
            plugins = meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
            plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
            for i in plugins:
                if not get_condvisibility(f'System.AddonIsEnabled({i})'):
                    break  # System doesn't have a required plugin so skip this player
            else:
                meta['plugin'] = plugins[0]
                players[file] = meta
    return players


def _get_dialog_players(players):
    return [
        ListItem(
            label=v.get('name'), label2=k,
            art={
                'thumb': v.get('icon', '').format(ADDONPATH)
                or KodiAddon(v.get('plugin', '')).getAddonInfo('icon')}).get_listitem()
        for k, v in sorted(players.items(), key=lambda i: try_int(i[1].get('priority')) or PLAYERS_PRIORITY)]


def _get_player_methods(player):
    methods = ['play_movie', 'play_episode', 'search_movie', 'search_episode']
    return [i for i in methods if i in player and player[i]]


def configure_players(*args, **kwargs):
    ConfigurePlayers().configure_players()


class _ConfigurePlayer():
    def __init__(self, player, filename):
        self.player = player
        self.filename = filename

    def get_player_settings(self):
        if not self.player:
            return
        # Name; Enable/Disable; Priority; is_resolvable; fallbacks(?)
        return [
            f'name: {self.player.get("name")}',
            f'disabled: {self.player.get("disabled", "false").lower()}',
            f'priority: {self.player.get("priority") or PLAYERS_PRIORITY}',
            f'is_resolvable: {self.player.get("is_resolvable", "select")}',
            f'make_playlist: {self.player.get("make_playlist", "false").lower()}',
            f'fallback: {dumps(self.player.get("fallback"))}',
            get_localized(32330),
            get_localized(190)]

    def set_name(self):
        name = self.player.get('name', '')
        name = Dialog().input(get_localized(32331).format(self.filename), defaultt=name)
        if not name:
            return
        self.player['name'] = name

    def set_disabled(self):
        disabled = 'false'
        if self.player.get('disabled', 'false').lower() == 'false':
            disabled = 'true'
        self.player['disabled'] = disabled

    def set_priority(self):
        priority = f'{self.player.get("priority") or PLAYERS_PRIORITY}'  # Input numeric takes str for some reason?!
        priority = Dialog().input(
            get_localized(32344).format(self.filename),
            defaultt=priority, type=INPUT_NUMERIC)
        priority = try_int(priority)
        if not priority:
            return
        self.player['priority'] = priority

    def set_resolvable(self):
        x = Dialog().select(get_localized(32332), [
            'setResolvedURL', 'PlayMedia', get_localized(32333)])
        if x == -1:
            return
        is_resolvable = 'select'
        if x == 0:
            is_resolvable = 'true'
        elif x == 1:
            if not Dialog().yesno(
                    get_localized(32339).format(self.filename),
                    get_localized(32340)):
                return self.set_resolvable()
            is_resolvable = 'false'
        self.player['is_resolvable'] = is_resolvable

    def set_makeplaylist(self):
        x = Dialog().yesno(get_localized(32424), get_localized(32425))
        if x == -1:
            return
        make_playlist = 'true' if x else 'false'
        self.player['make_playlist'] = make_playlist

    def _get_method_type(self, method):
        for i in ['movie', 'episode']:
            if i in method:
                return i

    def get_fallback_method(self, player, filename, og_method):
        """ Get the available methods for the player and ask user to select one """
        mt = self._get_method_type(og_method)
        methods = [
            f'{filename} {i}' for i in _get_player_methods(player) if mt in i
            and (filename != self.filename or i != og_method)]  # Avoid adding same fallback method as original
        if not methods:
            return
        x = Dialog().select(get_localized(32341), methods)
        if x == -1:
            return
        return methods[x]

    def get_fallback_player(self, og_method=None):
        # Get players from files and ask user to select one
        players = ConfigurePlayers()
        filename = players.select_player(get_localized(32343).format(self.filename, og_method))
        player = players.players.get(filename)
        if player and filename:
            return self.get_fallback_method(player, filename, og_method)

    def set_fallbacks(self):
        # Get the methods that the player supports and ask user to select which they want to set
        methods = _get_player_methods(self.player)
        x = Dialog().select(get_localized(32342).format(self.filename), [
            f'{i}: {self.player.get("fallback", {}).get(i, "null")}' for i in methods])
        if x == -1:
            return
        fallback = self.get_fallback_player(methods[x])
        if fallback:
            self.player.setdefault('fallback', {})[methods[x]] = fallback
        return self.set_fallbacks()

    def configure(self):
        """
        Returns player or -1 if reset to default (i.e. delete configured player)
        """
        x = Dialog().select(self.filename, self.get_player_settings())
        if x == -1:
            return self.player
        elif x == 0:
            self.set_name()
        elif x == 1:
            self.set_disabled()
        elif x == 2:
            self.set_priority()
        elif x == 3:
            self.set_resolvable()
        elif x == 4:
            self.set_makeplaylist()
        elif x == 5:
            self.set_fallbacks()
        elif x == 6:
            return -1
        elif x == 7:
            return self.player
        return self.configure()


class ConfigurePlayers():
    def __init__(self):
        with BusyDialog():
            self.players = get_players_from_file()
            self.dialog_players = _get_dialog_players(self.players)

    def select_player(self, header=get_localized(32328)):
        x = Dialog().select(header, self.dialog_players, useDetails=True)
        if x == -1:
            return
        return self.dialog_players[x].getLabel2()  # Filename is saved in label2

    def delete_player(self, filename):
        if not Dialog().yesno(
                get_localized(32334),
                get_localized(32335).format(filename),
                yeslabel=get_localized(13007), nolabel=get_localized(222)):
            return
        with BusyDialog():
            delete_file(PLAYERS_BASEDIR_SAVE, filename, join_addon_data=False)
            self.players = get_players_from_file()
            self.dialog_players = _get_dialog_players(self.players)

    def save_player(self, player, filename, confirm=True):
        if confirm and not Dialog().yesno(
                get_localized(32336), get_localized(32337).format(filename),
                yeslabel=get_localized(190), nolabel=get_localized(32338)):
            return
        with BusyDialog():
            self.players[filename] = player  # Update our players dictionary
            self.dialog_players = _get_dialog_players(self.players)  # Update our dialog list
            dumps_to_file(player, PLAYERS_BASEDIR_SAVE, filename, indent=4, join_addon_data=False)  # Write out file

    def configure_players(self):
        filename = self.select_player()
        if not filename:
            return
        player = deepcopy(self.players[filename])
        player = _ConfigurePlayer(player, filename=filename).configure()
        if player == -1:  # Reset player (i.e. delete player file)
            self.delete_player(filename)
        elif player and player != self.players[filename]:
            self.save_player(player, filename)
        return self.configure_players()
