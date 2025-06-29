from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.player.actions.keyboard import PlayerActionPluginKeyboard
from tmdbhelper.lib.player.actions.validation import PlayerActionValidation


class PlayerAction:  # Get path from actions iteration
    def __init__(
        self,
        player_meta,
        folder='',
        dialog=None,
        strict=None,
        **action
    ):
        # Parent class instance
        self.player_meta = player_meta

        # Setup data
        self.folder = self.string_format_map(folder)
        self.action = action or {}
        self.is_dialog = dialog
        self.is_strict = strict
        self.is_return = self.action.pop('return', None)  # Unable to capture as variable kwarg so pop instead

    @property
    def item(self):
        return self.player_meta.item

    def string_format_map(self, fmt):
        return fmt.format_map(self.item)

    def log(self, key, value):
        self.actions_log += (f'{key}: ', value, '\n')

    @cached_property
    def directory_generator(self):
        return (
            item for posx, item in enumerate(self.directory)
            if PlayerActionValidation(self, posx, item).is_valid
        )

    @cached_property
    def next_path(self):
        if not self.action:
            return
        if not self.is_strict:
            return next(self.directory_generator, None)

    @cached_property
    def directory(self):
        from tmdbhelper.lib.api.kodi.rpc import get_directory
        directory = get_directory(self.folder)

        self.log('FOLDER', self.folder)
        self.log('ACTION', self.action)

        # Kill keyboard inputter thread if still active and not used in get_directory
        self.player_meta.keyboard_thread.exit = True
        self.player_meta.null_keyboard_thread()

        return directory

    def run(self):
        if 'keyboard' in self.action:
            PlayerActionPluginKeyboard(self).run()
            return  # NOTE: Continue from here
        self.directory
