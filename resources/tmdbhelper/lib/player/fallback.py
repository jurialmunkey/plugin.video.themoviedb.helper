from jurialmunkey.ftools import cached_property


class PlayersFallback:

    def __init__(self, main, file, mode):
        self.main = main  # Main Players class
        self.file = file
        self.mode = mode

    @cached_property
    def meta(self):
        return self.main.players.get(self.file) if self.file and self.mode else None

    @cached_property
    def item(self):
        return self.main.item

    @cached_property
    def constructed_player(self):
        from tmdbhelper.lib.player.details.item import PlayerItemConstructed
        return PlayerItemConstructed(
            file=self.file,
            item=self.item,
            mode=self.mode,
            meta=self.meta
        ) if self.meta else None

    @cached_property
    def configured_item(self):
        return self.constructed_player.configured_item if self.constructed_player else None

    def player_check(self, player):
        if player.get('file') != self.constructed_player.file:
            return False
        if player.get('mode') != self.constructed_player.mode:
            return False
        return True

    @property
    def generator(self):
        return (x for x, player in enumerate(self.main.dialog_players) if self.player_check(player))

    @cached_property
    def idx(self):
        return next(self.generator, None)

    @cached_property
    def player(self):
        if self.configured_item is None:
            return

        if self.idx is not None:
            self.configured_item['idx'] = self.idx
            return self.configured_item

        return PlayersFallback(
            self.main,
            self.constructed_player.fallback_file,
            self.constructed_player.fallback_mode,
        ).player
