from jurialmunkey.ftools import cached_property
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


class PlayerSelectStandard:

    player_uid = None

    def __init__(self, players):
        self.players = players

    @cached_property
    def players_list(self):
        return self.players or []

    def players_generator(self, player_item=PlayerItem):
        return (player_item(i, x) for x, i in enumerate(self.players_list))

    def players_generated_list(self):
        return [
            j for j in self.players_generator()
            if self.player_uid is None or j.uid == self.player_uid
        ]

    @staticmethod
    def select_player(players_list, header=None, detailed=True):
        """ Select from a list of players """
        x = Dialog().select(
            header or get_localized(32042),
            [i.listitem for i in players_list],
            useDetails=detailed
        )
        return -1 if x == -1 else players_list[x].posx

    def get_player(self, x):
        player = self.players_list[x]
        player['idx'] = x
        return player

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed)
        return {} if x == -1 else self.get_player(x)


class PlayerSelectCombined(PlayerSelectStandard):
    @cached_property
    def players_combined_list(self):
        players_combined_dict = {j.uid: j for j in self.players_generator(PlayerItemCombined)}
        players_combined_list = [i for i in players_combined_dict.values()]
        return players_combined_list

    def select(self, header=None, detailed=True):
        """
        Select a player from the list
        """
        player = {}
        while not player:
            x = self.select_player(self.players_combined_list, header=header, detailed=detailed)
            if x == -1:
                break
            self.player_uid = self.players_combined_list[x].uid
            player = super().select(header, detailed)
        return player


class PlayerSelectModified(PlayerSelectStandard):
    @cached_property
    def players_list(self):
        players_list = [{
            'name': get_localized(32311),
            'plugin_name': 'plugin.video.themoviedb.helper',
            'plugin_icon': f'{ADDONPATH}/resources/icons/other/kodi.png'
        }]
        players_list = players_list + self.players
        return players_list
