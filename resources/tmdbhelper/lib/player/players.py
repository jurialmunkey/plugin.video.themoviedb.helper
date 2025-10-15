from xbmcgui import Dialog
from jurialmunkey.window import get_property
from jurialmunkey.parser import boolean
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import PLUGINPATH, format_folderpath, get_localized, get_setting
from tmdbhelper.lib.player.actions.resolver import ResolverPlayerSelect
from tmdbhelper.lib.addon.logger import kodi_log


class PlayersNext:

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

        return PlayersNext(
            self.main,
            self.constructed_player.fallback_file,
            self.constructed_player.fallback_mode,
        ).player


class Players:

    selected = None
    default_player = None
    tmdb_type = None
    season = None
    episode = None

    def __init__(
        self,
        islocal=False,
        player=None,
        mode=None,
        handle=None,
        **kwargs
    ):
        self.player = player  # the player file name
        self.mode = mode  # search or play
        self.handle = handle
        self.is_strm = islocal

    """
    Player hacks
    """

    @staticmethod
    def player_hacks_run(instance):
        try:
            instance.run()
        except AttributeError:
            return

    def player_hacks_update_listing_set(self, folder_path=None, reset_focus=None):
        from tmdbhelper.lib.player.phacks.update_listing import PlayerHacksUpdateListing
        self.player_hacks_update_listing = PlayerHacksUpdateListing(folder_path, reset_focus)

    def player_hacks_update_listing_run(self):
        self.player_hacks_run(self.player_hacks_update_listing)

    def player_hacks_resolved_url_set(self, listitem, action=None):
        from tmdbhelper.lib.player.phacks.resolved_url import PlayerHacksResolvedURL
        self.player_hacks_resolved_url = PlayerHacksResolvedURL(listitem, action, handle=self.handle, f_strm=self.is_strm, equeue=self.playqueue_next_episodes)

    def player_hacks_resolved_url_run(self):
        self.player_hacks_run(self.player_hacks_resolved_url)

    def player_hacks_playback_wait_set(self, fileext=None, timeout=5):
        from tmdbhelper.lib.player.phacks.playback_wait import PlayerHacksPlaybackWait
        self.player_hacks_playback_wait = PlayerHacksPlaybackWait(fileext, timeout)

    def player_hacks_playback_wait_run(self):
        self.player_hacks_run(self.player_hacks_playback_wait)

    """
    Properties
    """

    @cached_property
    def action_log(self):
        return []

    @cached_property
    def player_forced(self):
        from tmdbhelper.lib.player.player_id import PlayerId
        return PlayerId(self.tmdb_type, self.player, self.mode).player_id

    @cached_property
    def player_files(self):
        from tmdbhelper.lib.player.files import PlayerFiles
        return PlayerFiles(self.providers)

    @cached_property
    def players(self):
        return self.player_files.dictionary

    @cached_property
    def players_prioritised(self):
        return self.player_files.prioritise

    @cached_property
    def providers(self):
        try:
            return self.details.infoproperties['providers'].split(' / ')
        except (KeyError, AttributeError):
            return

    @cached_property
    def next_episodes(self):
        from tmdbhelper.lib.player.details.details import get_next_episodes
        return get_next_episodes(self.tmdb_id, self.season, self.episode, self.selected.player.file)

    @cached_property
    def item_kwargs(self):
        return {
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'season': self.season,
            'episode': self.episode,
        }

    @cached_property
    def details_dictionary(self):
        from tmdbhelper.lib.player.details.details import PlayerDetails
        return PlayerDetails(**self.item_kwargs)

    @cached_property
    def p_dialog_step_count(self):
        p_dialog_step_count = sum((
            int(self.p_dialog_step_is_enabled_recache_kodidb),
            int(self.p_dialog_step_is_enabled_player_details),
            int(self.p_dialog_step_is_enabled_dialog_players),
        ))
        return p_dialog_step_count

    @cached_property
    def p_dialog(self):
        from tmdbhelper.lib.addon.dialog import ProgressDialogPersistant
        return ProgressDialogPersistant('TMDbHelper', f'{get_localized(32374)}...', total=self.p_dialog_step_count)

    """
    ProgressDialog: Step 01: Build player details
    """

    p_dialog_step_is_enabled_player_details = True

    @cached_property
    def details(self):
        if not self.p_dialog_step_is_enabled_player_details:
            return
        with self.p_dialog as p_dialog:
            p_dialog.update(f'{get_localized(32375)}...')
            return self.details_dictionary[None]

    """
    ProgressDialog: Step 02: Recache Kodi DB
    """

    @cached_property
    def p_dialog_step_is_enabled_recache_kodidb(self):
        return bool(get_setting('default_player_kodi', 'int') and get_setting('force_recache_kodidb'))

    def recache_kodidb(self):
        if not self.p_dialog_step_is_enabled_recache_kodidb:
            return
        with self.p_dialog as p_dialog:
            p_dialog.update(f'{get_localized(32143)}...')
            from tmdbhelper.lib.script.method.maintenance import DatabaseMaintenance
            DatabaseMaintenance().recache_kodidb(notification=False)

    """
    ProgressDialog: Step 03: Build dialog players
    """

    p_dialog_step_is_enabled_dialog_players = True

    @cached_property
    def dialog_players(self):
        if not self.p_dialog_step_is_enabled_dialog_players:
            return

        self.recache_kodidb()

        with self.p_dialog as p_dialog:
            p_dialog.closing = True
            p_dialog.update(f'{get_localized(32376)}...')
            from tmdbhelper.lib.player.details.dialog import PlayersDialog
            return PlayersDialog(self.tmdb_type, item=self.item, data=self.players_prioritised).items

    @cached_property
    def item(self):
        from tmdbhelper.lib.player.details.details import PlayerDetailedItemDict
        return PlayerDetailedItemDict(**self.item_kwargs, details=self.details)

    @cached_property
    def chosen_default(self):
        from tmdbhelper.lib.player.method.userdefault import PlayerDefaultUserChoiceGetterFactory
        return PlayerDefaultUserChoiceGetterFactory(**self.item_kwargs).info

    def string_format_map(self, fmt):
        return fmt.format_map(self.item)  # NOTE: .format(**d) works in Py3.5 but not Py3.7+ so use format_map(d) instead

    def select_default(self, header=None, detailed=True):
        """ Returns user selected player via dialog - detailed bool switches dialog style """
        from tmdbhelper.lib.player.select import PlayerSelectAdditionalItems, PlayerSelectCombined
        self.p_dialog_step_is_enabled_player_details = False
        instance = PlayerSelectCombined(players=self.dialog_players)
        instance.additional_players = PlayerSelectAdditionalItems.clear_default_player()
        return instance.select(header=header, detailed=detailed)

    def get_player(self, name):
        file, mode = name.split()
        return PlayersNext(self, file, mode).player

    def get_default_player(self):
        """ Returns default player """

        if self.ignore_default:
            return

        if not self.dialog_players:
            return

        if self.player_forced:
            return self.get_player(self.player_forced)

        if self.chosen_default:
            return self.get_player(self.chosen_default)

        x = 0

        if self.dialog_players[x].get('is_local'):
            if get_setting('default_player_kodi', 'int') == 1:
                player = self.dialog_players[x]
                player['idx'] = x
                player['fallback'] = player.get('fallback') or self.default_player or ''  # Use default_player if this one fails
                return player

            if len(self.dialog_players) > 1:
                x = 1

        if self.dialog_players[x].get('is_provider'):
            if get_setting('default_player_provider'):
                player = self.dialog_players[x]
                player['idx'] = x
                player['fallback'] = player.get('fallback') or self.default_player or ''  # Use default_player if this one fails
                return player

        # No default player setting
        if not self.default_player:
            return

        return self.get_player(self.default_player)

    @cached_property
    def resolver(self):
        resolver = ResolverPlayerSelect(self.item, dialog_players=self.dialog_players, action_log=self.action_log)
        resolver.string_format_func = self.string_format_map  # TODO: Temp shim: move into class
        resolver.fallback_item_func = self.get_player  # TODO: Temp shim: move into class
        return resolver

    def get_resolved_metaitem(self, player=None, allow_default=False):
        self.resolver.update_player(self.get_default_player() if allow_default and not player else player)
        if not self.resolver.player:
            return
        self.selected = self.resolver
        return self.selected.item

    def get_resolved_listitem(self):
        if not self.item:
            return
        get_property('PlayerInfoString', clear_property=True)
        path = self.get_resolved_metaitem(allow_default=True) or {}
        self.details.params = {}
        self.details.path = path.pop('url', None)
        self.details.infoproperties.update(path)
        return self.details.get_listitem()

    def queue_next_episodes(self, route='make_upnext'):
        if not self.selected or self.selected.mode != 'play_episode':
            return
        if self.season is None or self.episode is None:
            return
        if not self.next_episodes or len(self.next_episodes) < 2:
            return

        self.player_hacks_playback_wait_set(True, timeout=30)
        self.player_hacks_playback_wait_run()

        if route == 'make_upnext':
            from tmdbhelper.lib.player.putils import make_upnext
            return make_upnext(self.next_episodes[0], self.next_episodes[1])
        if route == 'make_playlist':
            from tmdbhelper.lib.player.putils import make_playlist
            return make_playlist(self.next_episodes)

    def playqueue_next_episodes(self):
        make_playlist = self.selected.make_playlist
        if not make_playlist:
            return
        if make_playlist.lower() == 'upnext':
            self.queue_next_episodes(route='make_upnext')
            return
        if make_playlist.lower() == 'true':
            self.queue_next_episodes(route='make_playlist')
            return

    @cached_property
    def listitem(self):
        return self.get_resolved_listitem()

    @cached_property
    def listitem_path(self):
        if not self.listitem:
            return
        return self.listitem.getPath()

    @cached_property
    def action(self):
        return self.get_action()

    def get_action(self):
        if not self.listitem_path:
            return

        if self.listitem_path.startswith('executebuiltin://'):
            self.listitem.setProperty('is_folder', 'true')
            return self.listitem_path.replace('executebuiltin://', '')

        if self.listitem.getProperty('is_folder') == 'true':
            return format_folderpath(self.listitem_path)

        if not self.handle or self.listitem.getProperty('is_resolvable') == 'false':
            return self.listitem_path

        if self.listitem.getProperty('is_resolvable') == 'select' and not Dialog().yesno(
                f'{self.listitem.getProperty("player_name")} - {get_localized(32353)}',
                get_localized(32354),
                yeslabel=f'{get_localized(107)} (setResolvedURL)',
                nolabel=f'{get_localized(106)} (PlayMedia)'):
            return self.listitem_path

    def play(self, folder_path=None, reset_focus=None, ignore_default=False):
        self.ignore_default = boolean(ignore_default)

        if not self.listitem.getPath():
            return
        if self.listitem.getPath() == PLUGINPATH:
            return

        # Output action log
        kodi_log(self.action_log, 2)
        self.action_log = []

        # Reset folder hack
        self.player_hacks_update_listing_set(folder_path, reset_focus)
        self.player_hacks_update_listing_run()

        # Play item
        self.player_hacks_resolved_url_set(self.listitem, action=self.action)
        self.player_hacks_resolved_url_run()


class PlayersMovie(Players):
    tmdb_type = 'movie'

    def __init__(
        self,
        tmdb_id=None,
        **kwargs
    ):
        self.tmdb_id = tmdb_id
        super().__init__(**kwargs)

    @cached_property
    def default_player(self):
        return get_setting('default_player_movies', 'str')


class PlayersEpisode(Players):
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

    @cached_property
    def default_player(self):
        return get_setting('default_player_episodes', 'str')


def PlayersFactory(tmdb_type, **kwargs):
    if tmdb_type == 'movie':
        return PlayersMovie(**kwargs)

    if tmdb_type in ('tv', 'season', 'episode'):
        return PlayersEpisode(**kwargs)
