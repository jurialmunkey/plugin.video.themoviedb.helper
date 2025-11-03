from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class PlayerCustomiseSelectFallback:
    def __init__(self, dialog_item):
        self.dialog_item = dialog_item

    @cached_property
    def item_choice(self):
        x = Dialog().select(
            get_localized(32342).format(self.dialog_item.filename),
            [f'{name}: {data}' for name, data in self.dialog_item.fallback_methods]
        )
        return self.dialog_item.fallback_methods[x] if x != -1 else None

    @cached_property
    def new_player(self):
        if not self.item_choice:
            return
        from tmdbhelper.lib.player.config.customise.menu import PlayerCustomiseDialogMenuFallbacks
        return PlayerCustomiseDialogMenuFallbacks(self.item_choice[1]).choice

    @cached_property
    def new_filename(self):
        if not self.new_player:
            return
        return self.new_player.filename

    @cached_property
    def new_method(self):
        if not self.new_filename:
            return
        x = Dialog().select(get_localized(32341), self.new_player.methods)
        return self.new_player.methods[x] if x != -1 else None

    @cached_property
    def new_fallback(self):
        if self.new_filename == 'remove_fallback':
            return ''
        if not self.new_method:
            return
        return f'{self.new_filename} {self.new_method}'

    @cached_property
    def fallback(self):
        if self.new_fallback is None:
            return
        fallback = self.dialog_item.fallback
        if self.new_filename == 'remove_fallback':
            fallback.pop(self.item_choice[0], None)
        else:
            fallback[self.item_choice[0]] = self.new_fallback
        return fallback
