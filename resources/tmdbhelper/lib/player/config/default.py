from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class PlayerDefaultMovie:

    tmdb_type = 'movie'
    setting_name = 'default_player_movies'

    def __init__(self, header=None):
        self.header = header or get_localized(32476)

    @cached_property
    def player_files_prioritised(self):
        from tmdbhelper.lib.player.config.files import PlayerFiles
        return PlayerFiles().prioritise

    @cached_property
    def player_items(self):
        from tmdbhelper.lib.player.dialog.items import PlayerItems
        return PlayerItems(self.tmdb_type, item=None, data=self.player_files_prioritised)

    @cached_property
    def players_select_combined(self):
        from tmdbhelper.lib.player.dialog.combined import PlayerSelectCombined
        from tmdbhelper.lib.player.dialog.item.clear import PlayerItemClearDefault
        instance = PlayerSelectCombined(data=self.player_items)
        instance.additional_players = [PlayerItemClearDefault()]
        return instance

    @cached_property
    def choice(self):
        return self.players_select_combined.select(header=self.header, detailed=True)

    @property
    def setting_value(self):
        if not self.choice.file:
            return ''
        if not self.choice.mode:
            return ''
        return f'{self.choice.file} {self.choice.mode}'

    def select(self):
        if not self.choice:
            return
        from tmdbhelper.lib.addon.plugin import set_setting
        set_setting(self.setting_name, self.setting_value, 'str')


class PlayerDefaultEpisode(PlayerDefaultMovie):
    tmdb_type = 'tv'
    setting_name = 'default_player_episodes'


def PlayerDefault(tmdb_type):
    route = {
        'movie': PlayerDefaultMovie,
        'tv': PlayerDefaultEpisode,
        'season': PlayerDefaultEpisode,
        'episode': PlayerDefaultEpisode,
    }
    return route[tmdb_type]()
