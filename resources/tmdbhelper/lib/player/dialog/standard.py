from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.player.dialog.listitem import PlayerListItem
from xbmcgui import Dialog


class PlayerSelectStandard:

    player_uid = None
    additional_players = []

    def __init__(self, data):
        self.data = data

    @property
    def players(self):
        return self.data.items or []

    @property
    def players_list(self):
        players_list = self.additional_players + self.players
        return players_list

    def players_generator(self, player_item=PlayerListItem):
        return (player_item(i, x) for x, i in enumerate(self.players_list))

    @property
    def players_generated_list(self):
        return [
            j for j in self.players_generator()
            if self.player_uid is None or j.uid == self.player_uid
        ]

    @staticmethod
    def select_player(players_list, header=None, detailed=True, index=False):
        """ Select from a list of players """
        x = Dialog().select(
            header or get_localized(32042),
            [i.listitem for i in players_list],
            useDetails=detailed
        )
        return x if index or x == -1 else players_list[x].posx

    def get_player(self, x):
        return self.players_list[x]

    def select(self, header=None, detailed=True):
        """ Select a player from the list """
        x = self.select_player(self.players_generated_list, header=header, detailed=detailed)
        return {} if x == -1 else self.get_player(x)
