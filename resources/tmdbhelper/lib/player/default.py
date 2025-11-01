from jurialmunkey.ftools import cached_property


class PlayersDefault:

    def __init__(self, main):
        self.main = main  # Main Players class

    @cached_property
    def default_player_kodi(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return bool(get_setting('default_player_kodi', 'int') == 1)

    @cached_property
    def default(self):
        player = self.main.default_player
        return self.main.get_player(player)

    @cached_property
    def forced(self):
        from tmdbhelper.lib.player.player_id import PlayerId
        player = PlayerId(self.main.tmdb_type, self.main.player, self.main.mode).player_id
        return self.main.get_player(player)

    @cached_property
    def chosen(self):
        from tmdbhelper.lib.player.method.userdefault import PlayerDefaultUserChoiceGetterFactory
        player = PlayerDefaultUserChoiceGetterFactory(**self.main.item_kwargs).info
        return self.main.get_player(player)

    @cached_property
    def kodi(self):
        if not self.default_player_kodi:
            return
        try:
            return self.configure_player(next(self.kodi_generator))
        except StopIteration:
            return

    @cached_property
    def provider(self):
        try:
            return self.configure_player(next(self.provider_generator))
        except StopIteration:
            return

    @cached_property
    def kodi_generator(self):
        return self.get_generator('is_local')

    @cached_property
    def provider_generator(self):
        return self.get_generator('is_provider')

    def configure_player(self, x):
        try:
            player = self.main.dialog_players[x]
            player['idx'] = x
            return player
        except TypeError:
            return

    def get_next_fallback(self):
        player = self.get_next_player()
        return f'{player["file"]} {player["mode"]}' if player else ''

    def get_generator(self, key):
        return (x for x, i in enumerate(self.main.dialog_players) if i.get(key))

    @cached_property
    def priority(self):
        return (i for i in (f() for f in (
            lambda: self.forced,
            lambda: self.chosen,
            lambda: self.kodi,
            lambda: self.provider,
            lambda: self.default,
        )) if i)

    @cached_property
    def player(self):
        return self.get_next_player()

    def get_next_player(self):
        try:
            player = next(self.priority)
            player['fallback'] = player.get('fallback') or self.get_next_fallback()
            return player
        except StopIteration:
            return
