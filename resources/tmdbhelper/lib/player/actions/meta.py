from tmdbhelper.lib.files.ftools import cached_property
# from tmdbhelper.lib.player.actions.keyboard import PlayerActionPluginKeyboard
# from tmdbhelper.lib.player.actions.validation import PlayerActionValidation


class NullObject:
    pass


class PlayerMeta:
    def __init__(
        self,
        item,
        actions=None,
        is_local=False,
        is_folder=False,
        **kwargs
    ):
        self.null_keyboard_thread()
        self.actions = actions or {}
        self.is_local = bool(is_local)
        self.is_folder = bool(is_folder)
        self.item = item

    def null_keyboard_thread(self):
        self.keyboard_thread = NullObject()

    @cached_property
    def path(self):
        if not self.actions:
            return
        if isinstance(self.actions, list):
            return   # self._get_path_from_actions(actions)
        if isinstance(self.actions, str):  # Single item not a list so just return formatted
            return self.actions if self.is_local else self.actions.format_map(self.item)
