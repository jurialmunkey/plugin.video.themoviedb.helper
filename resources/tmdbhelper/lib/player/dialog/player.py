from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting
from tmdbhelper.lib.script.method.decorators import get_tmdb_id, map_kwargs
from tmdbhelper.lib.addon.logger import kodi_log


class Player:

    selected = None
    ignore_default = False
    tmdb_type = None
    season = None
    episode = None

    def __init__(
        self,
        handle=None,
        player=None,
        mode=None,
        **kwargs
    ):
        self.player = player  # the player file name
        self.mode = mode  # search or play
        self.handle = handle  # Handle from plugin callback hook

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
            file=self.player,
            mode=self.mode,
        )
        player_default.ignore_default = self.ignore_default
        return player_default

    @cached_property
    def player_select(self):
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
        return self.get_next_player()

    def get_next_player(self, fallback=None):
        player = None
        player = self.player_default.get_player_by_info(fallback)

        try:
            player = player or next(self.player_default.queue)
        except StopIteration:
            player = player or self.player_select.select(detailed=True)

        if not player:
            return

        from tmdbhelper.lib.player.action.resolver import PlayerResolver
        player.resolver = PlayerResolver(player, handle=self.handle)

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
        self.initialise_setup()

        while self.player_current and not self.xbmc_monitor.abortRequested():
            self.play_loop()

        if self.player_current:
            return kodi_log(f'lib.player - Aborted!', 1)

        if self.player_current is None:
            return kodi_log(f'lib.player - Failure!', 1)

        kodi_log(f'lib.player - Success!', 1)

    def play_loop(self):

        kodi_log(f'lib.player - {self.player_current.name}: Attempting to resolve...', 1)

        if not self.player_current.resolver.path:
            kodi_log(f'lib.player - {self.player_current.name}: Failed to resolve!', 1)
            self.player_items.del_player(self.player_current)
            self.player_current = self.get_next_player(self.player_current.fallback)
            return

        # self.test()
        kodi_log(f'lib.player - {self.player_current.name}: Resolved\n{self.player_current.resolver.path} {self.player_current.resolver.is_folder}', 1)
        self.reupdate_listing()
        self.player_current.resolver.run()
        self.player_current = False

    @staticmethod
    def reupdate_listing():
        from tmdbhelper.lib.player.action.reupdate import PlayerReUpdateListing
        PlayerReUpdateListing().run()

    def test(self):
        data = [
            ('RT', self.translation),
            ('DT', self.details),
            ('KD', self.recached_kodidb),
            ('PP', self.providers),
            ('PD', self.player_current.name),
            ('PF', self.player_current.resolver.path),
            ('PF', self.player_current.resolver.is_folder),
        ]

        Dialog().textviewer('OUTPUT', '\n'.join([f'{k}: {v}' for k, v in data]))


class PlayerMovie(Player):
    tmdb_type = 'movie'

    def __init__(
        self,
        tmdb_id=None,
        **kwargs
    ):
        self.tmdb_id = tmdb_id
        super().__init__(**kwargs)


class PlayerEpisode(Player):
    tmdb_type = 'tv'

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


@map_kwargs({'play': 'tmdb_type'})
@get_tmdb_id
def player_play(ignore_default=False, **kwargs):
    from jurialmunkey.parser import boolean
    kodi_log(['player_play - attempting to play\n', kwargs], 1)
    player = Player(**kwargs)
    player.ignore_default = boolean(ignore_default)
    player.play()
