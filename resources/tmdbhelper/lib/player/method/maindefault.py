from jurialmunkey.ftools import cached_property


class PlayerDefaultMainChoiceMovie:

    tmdb_type = 'movie'
    setting_name = 'default_player_movies'

    def __init__(self, header='Select default'):
        self.header = header

    @cached_property
    def player_files_prioritised(self):
        from tmdbhelper.lib.player.files import PlayerFiles
        return PlayerFiles().prioritise

    @cached_property
    def players_dialog_items(self):
        from tmdbhelper.lib.player.details.dialog import PlayersDialog
        return PlayersDialog(self.tmdb_type, item=None, data=self.player_files_prioritised).items

    @cached_property
    def players_select_combined(self):
        from tmdbhelper.lib.player.select import PlayerSelectAdditionalItems, PlayerSelectCombined
        instance = PlayerSelectCombined(players=self.players_dialog_items)
        instance.additional_players = PlayerSelectAdditionalItems.clear_default_player()
        return instance

    @cached_property
    def choice(self):
        return self.players_select_combined.select(header=self.header, detailed=True)

    @property
    def choice_file(self):
        return self.choice.get('file')

    @property
    def choice_mode(self):
        return self.choice.get('mode')

    @property
    def setting_value(self):
        if not self.choice_file:
            return ''
        if not self.choice_mode:
            return ''
        return f'{self.choice_file} {self.choice_mode}'

    def select(self):
        if not self.choice:
            return
        from tmdbhelper.lib.addon.plugin import set_setting
        set_setting(self.setting_name, self.setting_value, 'str')


class PlayerDefaultMainChoiceEpisode(PlayerDefaultMainChoiceMovie):
    tmdb_type = 'tv'
    setting_name = 'default_player_episodes'


def PlayerDefaultMainChoiceFactory(tmdb_type):
    route = {
        'movie': PlayerDefaultMainChoiceMovie,
        'tv': PlayerDefaultMainChoiceEpisode,
        'season': PlayerDefaultMainChoiceEpisode,
        'episode': PlayerDefaultMainChoiceEpisode,
    }
    return route[tmdb_type]()


def set_defaultplayer(set_defaultplayer, **kwargs):
    return PlayerDefaultMainChoiceFactory(set_defaultplayer).select()
