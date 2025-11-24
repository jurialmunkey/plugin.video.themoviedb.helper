from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.futils import get_files_in_folder
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.addon.consts import (
    PLAYERS_BASEDIR_BUNDLED,
    PLAYERS_BASEDIR_USER,
    PLAYERS_BASEDIR_SAVE,
)


class PlayerFiles:

    basedir_user = PLAYERS_BASEDIR_USER
    basedir_save = PLAYERS_BASEDIR_SAVE

    def __init__(self, providers=None, show_disabled=False):
        self.providers = providers
        self.show_disabled = show_disabled

    @cached_property
    def basedir_bundled(self):
        if not get_setting('bundled_players'):
            return
        return PLAYERS_BASEDIR_BUNDLED

    @cached_property
    def basedirs(self):
        basedirs = [i for i in (
            self.basedir_user,
            self.basedir_bundled,
            self.basedir_save,
        ) if i]
        return basedirs

    @cached_property
    def player_file_and_path_list(self):
        return {
            filename: folder
            for folder in self.basedirs
            for filename in get_files_in_folder(folder, r'.*\.json')
        }

    @cached_property
    def player_file_metadata_list(self):
        from tmdbhelper.lib.player.config.meta import PlayerMeta
        return [
            PlayerMeta(folder, filename, self.providers, self.show_disabled)
            for filename, folder in self.player_file_and_path_list.items()
        ]

    @cached_property
    def requires_translation(self):
        return any((
            i.requires_translation
            for i in self.player_file_metadata_list
            if i.is_enabled
        ))

    @cached_property
    def dictionary(self):
        return {
            i.filename: i.metadata
            for i in self.player_file_metadata_list
            if i.is_enabled
        }

    @cached_property
    def prioritise(self):
        return [
            (i.filename, i.metadata)
            for i in sorted(self.player_file_metadata_list, key=lambda x: (x.priority, x.plugin))
            if i.is_enabled
        ]
