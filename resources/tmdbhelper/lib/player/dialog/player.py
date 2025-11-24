from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting
from tmdbhelper.lib.addon.logger import kodi_log


class Player:

    selected = None
    ignore_default = False
    allow_playlist = True
    tmdb_type = None
    season = None
    episode = None
    mode_affix = 'null'

    def __init__(
        self,
        handle=None,
        player=None,
        mode=None,
        **kwargs
    ):
        self.player_file = player  # the player file name
        self.player_mode = mode  # search or play
        self.handle = handle  # Handle from plugin callback hook

    @property
    def player_mode(self):
        return self._player_mode

    @player_mode.setter
    def player_mode(self, value):
        self._player_mode = f'{value}_{self.mode_affix}' if value else None

    """
    Init Setup Steps
    """

    def initialise_setup(self):
        for i in (
            lambda: self.translation,
            lambda: self.details,
            self.recache_library,
            lambda: self.players,
        ):
            i()

    """
    ProgressDialog
    """

    @cached_property
    def p_dialog(self):
        from tmdbhelper.lib.addon.dialog import ProgressDialogPersistant
        return ProgressDialogPersistant('TMDbHelper', f'{get_localized(32374)}...', total=4)

    """
    ProgressDialog: Step 01: Check translation flags
    """

    @cached_property
    def translation(self):
        with self.p_dialog as p_dialog:
            p_dialog.update(f'{get_localized(32144)}...')
            return self.player_files_data.requires_translation

    """
    ProgressDialog: Step 02: Build player details
    """

    @cached_property
    def details(self):
        with self.p_dialog as p_dialog:
            p_dialog.update(f'{get_localized(32375)}...')
            return self.player_details.details

    """
    ProgressDialog: Step 03: Recache Kodi Library DB
    """

    def recache_library(self):
        with self.p_dialog as p_dialog:
            p_dialog.update(f'{get_localized(32145)}...')
            return self.recached_kodidb

    """
    ProgressDialog: Step 04: Build dialog players
    """

    @cached_property
    def players(self):
        with self.p_dialog as p_dialog:
            p_dialog.closing = True
            p_dialog.update(f'{get_localized(32376)}...')
            return self.player_items.items

    """
    Settings
    """

    @cached_property
    def force_recache_kodidb(self):
        return bool(get_setting('default_player_kodi', 'int') and get_setting('force_recache_kodidb'))

    @cached_property
    def combined_players(self):
        return get_setting('combined_players')

    """
    Kodi DB
    """

    @cached_property
    def recached_kodidb(self):
        if not self.force_recache_kodidb:
            return False
        from tmdbhelper.lib.script.method.maintenance import DatabaseMaintenance
        DatabaseMaintenance().recache_kodidb(notification=False)
        return True

    """
    PlayerFiles
    """

    @cached_property
    def player_files_data(self):
        from tmdbhelper.lib.player.config.files import PlayerFiles
        return PlayerFiles()

    @cached_property
    def player_files(self):
        from tmdbhelper.lib.player.config.files import PlayerFiles
        player_files = PlayerFiles(self.providers)
        player_files.player_file_and_path_list = self.player_files_data.player_file_and_path_list  # Skip reread files
        return player_files

    """
    PlayerDialog
    """

    @cached_property
    def player_items(self):
        from tmdbhelper.lib.player.dialog.items import PlayerItems
        return PlayerItems(self.tmdb_type, item=self.dictionary, data=self.player_files.prioritise)

    @cached_property
    def player_default(self):
        from tmdbhelper.lib.player.dialog.default import PlayerDefault
        player_default = PlayerDefault(
            self.tmdb_type,
            data=self.player_items,
            user=self.player_chosen,
            file=self.player_file,
            mode=self.player_mode,
        )
        player_default.ignore_default = self.ignore_default
        return player_default

    @cached_property
    def player_select(self):
        if not self.combined_players:
            return self.get_player_select_standard()
        return self.get_player_select_combined()

    def get_player_select_standard(self):
        from tmdbhelper.lib.player.dialog.standard import PlayerSelectStandard
        return PlayerSelectStandard(data=self.player_items)

    def get_player_select_combined(self):
        from tmdbhelper.lib.player.dialog.combined import PlayerSelectCombined
        return PlayerSelectCombined(data=self.player_items)

    @cached_property
    def player_chosen(self):
        from tmdbhelper.lib.player.config.chosen import PlayerChosenGet
        return PlayerChosenGet(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season,
            episode=self.episode
        )

    @cached_property
    def player_current(self):
        self.initialise_setup()
        return self.get_player()

    def get_player(self, fallback=None):
        player = None
        player = self.player_default.get_player_by_info(fallback)
        player = player or self.get_next_player_default()
        player = player or self.player_select.select(detailed=True)
        return self.set_resolver(player) if player else None

    def get_next_player_default(self):
        try:
            return next(self.player_default.queue)
        except StopIteration:
            return

    def set_resolver(self, player):
        from tmdbhelper.lib.player.action.resolver import PlayerResolver
        player.resolver = PlayerResolver(player, handle=self.handle)
        player.resolver.allow_playlist = self.allow_playlist
        return player

    """
    PlayerDetails
    """

    @cached_property
    def player_details(self):
        from tmdbhelper.lib.player.dialog.details import PlayerDetails
        return PlayerDetails(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season,
            episode=self.episode,
            translation=self.translation
        )

    @cached_property
    def providers(self):
        try:
            providers = self.details.infoproperties['providers']
            return providers.split(' / ') if providers else None
        except (KeyError, AttributeError):
            return

    @cached_property
    def dictionary(self):
        from tmdbhelper.lib.player.dialog.dictionary import PlayerDictionary
        return PlayerDictionary(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season,
            episode=self.episode,
            details=self.details
        )

    """
    Play
    """
    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    def play(self):
        while self.player_current and not self.xbmc_monitor.abortRequested():
            self.loop()

        if self.player_current:
            return kodi_log(f'lib.player - Aborted!', 1)

        if self.player_current is None:
            return kodi_log(f'lib.player - Failure!', 1)

        kodi_log(f'lib.player - Success!', 1)

    def loop(self):

        kodi_log([
            f'lib.player - {self.player_current.name}: Resolving...\n',
            f'{self.player_current.file} {self.player_current.mode}\n',
            f'{self.player_current.resolver.path}'], 1)

        if not self.player_current.resolver.path:
            return self.more()

        from tmdbhelper.lib.player.action.reupdate import PlayerReUpdateListing
        PlayerReUpdateListing().run()

        if not self.player_current.resolver.success:
            return self.more()

        self.player_current = False

    def more(self):
        self.player_items.del_player(self.player_current)
        self.player_current = self.get_player(self.player_current.fallback)


class PlayerMovie(Player):
    tmdb_type = 'movie'
    mode_affix = 'movie'

    def __init__(
        self,
        tmdb_id=None,
        **kwargs
    ):
        self.tmdb_id = tmdb_id
        super().__init__(**kwargs)


class PlayerEpisode(Player):
    tmdb_type = 'tv'
    mode_affix = 'episode'

    def __init__(
        self,
        tmdb_id=None,
        season=None,
        episode=None,
        **kwargs
    ):
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        super().__init__(**kwargs)


def Player(tmdb_type, **kwargs):
    if tmdb_type == 'movie':
        return PlayerMovie(**kwargs)

    if tmdb_type in ('tv', 'season', 'episode'):
        return PlayerEpisode(**kwargs)
