from jurialmunkey.ftools import cached_property


class PlayerDefaultBasic:

    ignore_default = False

    def __init__(self, data, file=None, mode=None, user=None):
        self.data = data  # PlayerItems class
        self.file = file  # Forced file
        self.mode = mode  # Forced mode
        self.user = user  # PlayerChosenGet class

    """
    Settings
    """

    @cached_property
    def default_player_kodi(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return bool(get_setting('default_player_kodi', 'int') == 1)

    @cached_property
    def default_player(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return get_setting(self.default_player_setting, 'str')

    default_player_setting = ''

    @cached_property
    def chosen_player(self):
        try:
            return self.user.info
        except AttributeError:
            return

    """
    Outputs
    """

    @cached_property
    def forced(self):
        if not self.file or not self.mode:
            return
        return self.get_player_by_info(f'{self.file} {self.mode}')

    @cached_property
    def default(self):
        return self.get_player_by_info(self.default_player)

    @cached_property
    def kodi(self):
        if not self.default_player_kodi:
            return
        return self.get_generator_next(self.get_generator_by_attr('is_local'))

    @cached_property
    def chosen(self):
        return self.get_player_by_info(self.chosen_player)

    """
    Locator
    """

    def get_player_by_info(self, info):
        try:
            file, mode = info.split()
        except (AttributeError, ValueError):
            return
        if not file or not mode:
            return
        return self.get_generator_next(
            player for player in self.data.items
            if player.file == file and player.mode == mode
        )

    def get_generator_next(self, generator):
        try:
            return next(generator)
        except StopIteration:
            return

    def get_generator_by_attr(self, attr):
        return (
            player for player in self.data.items
            if getattr(player, attr)
        )

    @cached_property
    def player_provider_generator(self):
        return self.get_generator_by_attr('is_provider')

    """
    Priority
    """

    @cached_property
    def queue(self):
        return (i for i in (f() for f in self.queue_generator) if i)

    @cached_property
    def queue_generator(self):
        return (
            lambda: self.forced,
            lambda: self.chosen,
            lambda: self.kodi,
            lambda: self.get_generator_next(self.player_provider_generator),
            lambda: self.get_generator_next(self.player_provider_generator),
            lambda: self.get_generator_next(self.player_provider_generator),
            lambda: self.get_generator_next(self.player_provider_generator),
            lambda: self.get_generator_next(self.player_provider_generator),
            lambda: self.default,
        ) if not self.ignore_default else (
            lambda: self.forced,
        )


class PlayerDefaultMovie(PlayerDefaultBasic):
    tmdb_type = 'movie'
    default_player_setting = 'default_player_movies'


class PlayerDefaultEpisode(PlayerDefaultBasic):
    tmdb_type = 'tv'
    default_player_setting = 'default_player_episodes'


def PlayerDefault(tmdb_type, **kwargs):
    if tmdb_type == 'movie':
        return PlayerDefaultMovie(**kwargs)

    if tmdb_type in ('tv', 'season', 'episode'):
        return PlayerDefaultEpisode(**kwargs)
