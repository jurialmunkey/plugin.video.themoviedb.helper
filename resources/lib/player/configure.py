import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.helpers.constants import PLAYERS_BASEDIR_BUNDLED, PLAYERS_BASEDIR_USER, PLAYERS_BASEDIR_SAVE, PLAYERS_PRIORITY
from resources.lib.helpers.fileutils import get_files_in_folder
from resources.lib.helpers.plugin import ADDON, ADDONPATH, viewitems
from resources.lib.helpers.fileutils import read_file, dumps_to_file, delete_file
from resources.lib.helpers.parser import try_int
from resources.lib.items.listitem import ListItem
from resources.lib.helpers.decorators import busy_dialog
from json import loads


def get_players_from_file():
    players = {}
    basedirs = [PLAYERS_BASEDIR_USER]
    if ADDON.getSettingBool('bundled_players'):
        basedirs += [PLAYERS_BASEDIR_BUNDLED]
    basedirs += [PLAYERS_BASEDIR_SAVE]  # Add saved players last so they overwrite
    for basedir in basedirs:
        files = get_files_in_folder(basedir, r'.*\.json')
        for file in files:
            meta = loads(read_file(basedir + file)) or {}
            plugins = meta.get('plugin') or 'plugin.undefined'  # Give dummy name to undefined plugins so that they fail the check
            plugins = plugins if isinstance(plugins, list) else [plugins]  # Listify for simplicity of code
            for i in plugins:
                if not xbmc.getCondVisibility(u'System.HasAddon({0})'.format(i)):
                    break  # System doesn't have a required plugin so skip this player
            else:
                players[file] = meta
    return players


def _get_dialog_players(players):
    return [
        ListItem(
            label=v.get('name'), label2=k,
            art={
                'thumb': v.get('icon', '').format(ADDONPATH)
                or xbmcaddon.Addon(v.get('plugin', '')).getAddonInfo('icon')}).get_listitem()
        for k, v in sorted(viewitems(players), key=lambda i: try_int(i[1].get('priority')) or PLAYERS_PRIORITY)]


def configure_players(**kwargs):
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
            'name: {}'.format(self.player.get('name')),
            'disabled: {}'.format(self.player.get('disabled', 'false').lower()),
            'priority: {}'.format(self.player.get('priority') or PLAYERS_PRIORITY),
            'is_resolvable: {}'.format(self.player.get('is_resolvable', 'select')),
            '',  # TODO: Fallbacks will go here
            ADDON.getLocalizedString(32330),
            xbmc.getLocalizedString(190)]

    def set_name(self):
        name = self.player.get('name', '')
        name = xbmcgui.Dialog().input(ADDON.getLocalizedString(32331).format(self.filename), defaultt=name)
        if not name:
            return
        self.player['name'] = name

    def set_disabled(self):
        disabled = 'false'
        if self.player.get('disabled', 'false').lower() == 'false':
            disabled = 'true'
        self.player['disabled'] = disabled

    def set_priority(self):
        priority = '{}'.format(self.player.get('priority') or PLAYERS_PRIORITY)  # Input numeric takes str for some reason?!
        priority = xbmcgui.Dialog().input(
            'Enter New Priority for {}'.format(self.filename),
            defaultt=priority, type=xbmcgui.INPUT_NUMERIC)
        priority = try_int(priority)
        if not priority:
            return
        self.player['priority'] = priority

    def set_resolvable(self):
        x = xbmcgui.Dialog().select(ADDON.getLocalizedString(32332), [
            'setResolvedURL', 'PlayMedia', ADDON.getLocalizedString(32333)])
        if x == -1:
            return
        is_resolvable = 'select'
        if x == 0:
            is_resolvable = 'true'
        elif x == 1:
            if not xbmcgui.Dialog().yesno(
                    ADDON.getLocalizedString(32339).format(self.filename),
                    ADDON.getLocalizedString(32340)):
                return self.set_resolvable()
            is_resolvable = 'false'
        self.player['is_resolvable'] = is_resolvable

    def configure(self):
        """
        Returns player or -1 if reset to default (i.e. delete configured player)
        """
        x = xbmcgui.Dialog().select(self.filename, self.get_player_settings())
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
            pass  # Add fallbacks here
        elif x == 5:
            return -1
        elif x == 6:
            return self.player
        return self.configure()


class ConfigurePlayers():
    def __init__(self):
        self.players = get_players_from_file()
        self.dialog_players = _get_dialog_players(self.players)

    def select_player(self):
        x = xbmcgui.Dialog().select(ADDON.getLocalizedString(32328), self.dialog_players, useDetails=True)
        if x == -1:
            return
        return self.dialog_players[x].getLabel2()  # Filename is saved in label2

    def delete_player(self, filename):
        if not xbmcgui.Dialog().yesno(
                ADDON.getLocalizedString(32334),
                ADDON.getLocalizedString(32335).format(filename),
                yeslabel=xbmc.getLocalizedString(13007), nolabel=xbmc.getLocalizedString(222)):
            return
        with busy_dialog():
            delete_file(PLAYERS_BASEDIR_SAVE, filename, join_addon_data=False)
            self.players = get_players_from_file()
            self.dialog_players = _get_dialog_players(self.players)

    def save_player(self, player, filename, confirm=True):
        if confirm and not xbmcgui.Dialog().yesno(
                ADDON.getLocalizedString(32336), ADDON.getLocalizedString(32337).format(filename),
                yeslabel=xbmc.getLocalizedString(190), nolabel=ADDON.getLocalizedString(32338)):
            return
        with busy_dialog():
            self.players[filename] = player  # Update our players dictionary
            self.dialog_players = _get_dialog_players(self.players)  # Update our dialog list
            dumps_to_file(player, PLAYERS_BASEDIR_SAVE, filename, indent=4, join_addon_data=False)  # Write out file

    def configure_players(self):
        filename = self.select_player()
        if not filename:
            return
        player = self.players[filename].copy()
        player = _ConfigurePlayer(player, filename=filename).configure()
        if player == -1:  # Reset player (i.e. delete player file)
            self.delete_player(filename)
        elif player and player != self.players[filename]:
            self.save_player(player, filename)
        return self.configure_players()
