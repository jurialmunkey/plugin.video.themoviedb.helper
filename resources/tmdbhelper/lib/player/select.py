from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_localized
from xbmcgui import Dialog


class PlayerItem:
    def __init__(self, meta, posx):
        self.meta = meta
        self.posx = posx

    @cached_property
    def name(self):
        return self.meta.get('name')

    @cached_property
    def uid(self):
        if self.plugin_name == 'xbmc.core':
            return self.name
        return self.plugin_name

    @cached_property
    def plugin_name(self):
        return self.meta['plugin_name']

    @cached_property
    def label(self):
        return self.name

    @cached_property
    def label2(self):
        return self.plugin_name

    @cached_property
    def art(self):
        return {'thumb': self.meta.get('plugin_icon')}

    @cached_property
    def item(self):
        return {
            'label': self.label,
            'label2': self.label2,
            'art': self.art,
        }

    @cached_property
    def listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(**self.item).get_listitem()


class PlayerItemCombined(PlayerItem):
    @cached_property
    def label(self):
        if self.plugin_name == 'xbmc.core':
            return self.name
        from xbmcaddon import Addon as KodiAddon
        return KodiAddon(self.plugin_name).getAddonInfo('name')


class PlayerSelect:
    def __init__(self, players, header=None, detailed=True):
        self.players = players
        self.header = header or get_localized(32042)
        self.detailed = detailed

    @cached_property
    def players_list(self):
        return self.players or []

    def players_generator(self, player_item=PlayerItem):
        return (player_item(i, x) for x, i in enumerate(self.players_list))

    @cached_property
    def players_combined_list(self):
        players_combined_dict = {j.uid: j for j in self.players_generator(PlayerItemCombined)}
        players_combined_list = [i for i in players_combined_dict.values()]
        return players_combined_list

    def get_players_list_by_uid(self, uid=None):
        return [
            j for j in self.players_generator()
            if uid is None or j.uid == uid
        ]

    def select_standard_player(self, uid=None):
        """
        Select from a list of players
        Set a UID to only display players for a single plugin
        """
        player_list = self.get_players_list_by_uid(uid)
        x = Dialog().select(
            self.header,
            [i.listitem for i in player_list],
            useDetails=self.detailed
        )
        return -1 if x == -1 else player_list[x].posx

    def select_combined_player(self):
        """
        Combine players from same plugin into a subfolder before selecting
        Used to reduce overall size of player list to specific plugins
        """
        player_list = self.players_combined_list
        x = Dialog().select(
            self.header,
            [i.listitem for i in player_list],
            useDetails=self.detailed
        )
        if x == -1:
            return -1
        x = self.select_standard_player(player_list[x].uid)
        return self.select_combined_player() if x == -1 else x

    def select(self, combined=False):
        """
        Select a player from the list
        Use combined bool to display each plugin as a separate subfolder of players
        """
        x = self.select_combined_player() if combined else self.select_standard_player()
        if x == -1:
            return {}
        player = self.players_list[x]
        player['idx'] = x
        return player


class PlayerSelectWithClearDefault(PlayerSelect):
    @cached_property
    def players_list(self):
        players_list = [{
            'name': get_localized(32311),
            'plugin_name': 'plugin.video.themoviedb.helper',
            'plugin_icon': f'{ADDONPATH}/resources/icons/other/kodi.png'
        }]
        players_list = players_list + self.players
        return players_list
