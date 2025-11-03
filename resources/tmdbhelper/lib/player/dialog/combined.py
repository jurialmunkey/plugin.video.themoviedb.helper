from tmdbhelper.lib.player.dialog.listitem import PlayerListItemCombined
from tmdbhelper.lib.player.dialog.standard import PlayerSelectStandard


class PlayerSelectCombined(PlayerSelectStandard):
    @property
    def players_combined_list(self):
        players_combined_dict = {j.uid: j for j in self.players_generator(PlayerListItemCombined)}
        players_combined_list = [i for i in players_combined_dict.values()]
        return players_combined_list

    def select_from_group(self, group, header=None, detailed=True):
        if len(self.players_generated_list) != 1:
            return super().select(header, detailed)
        if group.player.plugin_name != 'plugin.video.themoviedb.helper':
            return super().select(header, detailed)
        return self.get_player(group.posx)

    def set_current_group(self, x):
        group = self.players_combined_list[x]
        self.player_uid = group.uid
        return group

    def select(self, header=None, detailed=True):
        """
        Select a player from the list
        """
        player = {}

        while not player:

            x = self.select_player(
                self.players_combined_list,
                header=header,
                detailed=detailed,
                index=True
            )

            if x == -1:
                break

            player = self.select_from_group(self.set_current_group(x))

        return player
