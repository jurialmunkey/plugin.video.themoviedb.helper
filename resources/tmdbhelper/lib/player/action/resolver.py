from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import executebuiltin, format_folderpath
from tmdbhelper.lib.addon.logger import kodi_log


PLAYER_ACTION_TYPE_NONE = 0
PLAYER_ACTION_TYPE_LIST = 1
PLAYER_ACTION_TYPE_FSTR = 2


class PlayerResolverBase:

    """
    Kodi does 5x retries to resolve url if isPlayable property is set - strm files force this property.
    However, external plugins might not resolve directly to URL and instead might require PlayMedia.
    Also, if external plugin endpoint is a folder we need to do ActivateWindow/Container.Update instead.
    Passing False to setResolvedUrl doesn't work correctly and the retry is triggered anyway.
    In these instances we use a hack to avoid the retry by first resolving to a dummy file instead.
    """

    def __init__(self, player, handle=None):
        self.player = player
        self.handle = handle

    next_episodes_list = None
    resolved_dummyfile = False

    def update_playerstring(self):
        from tmdbhelper.lib.player.action.playerstring import load_playerstring
        kodi_log(['lib.player - playerstring:\n', f'{load_playerstring(self.listitem)}'], 1)

    def update_episodequeue(self):
        if not self.player.make_playlist:
            kodi_log(f'lib.player - Playlist: Not Enabled', 1)
            return

        if not self.next_episodes_list:
            kodi_log(f'lib.player - Playlist: No Next Episodes', 1)
            return

        kodi_log(f'lib.player - Playlist: Adding {len(self.next_episodes_list)} episodes', 1)
        self.next_episodes.update()

    """
    setResolvedUrl
    """

    def execute_seturl(self):
        self.update_episodequeue()
        from xbmcplugin import setResolvedUrl
        kodi_log(['lib.player - resolving path to url\n', self.path], 1)
        setResolvedUrl(self.handle, True, self.listitem)
        self.update_playerstring()

    @property
    def on_seturl(self):
        if not self.path:
            return False
        if self.is_folder:
            return False
        if not self.listitem:
            return False
        return True

    """
    Player
    """

    def execute_player(self):
        self.update_episodequeue()
        from xbmc import Player
        kodi_log(['lib.player - playing path with xbmc.Player():\n', self.action], 1)
        Player().play(self.action, self.listitem)
        self.update_playerstring()

    @property
    def on_player(self):
        if not self.path:
            return False
        if self.is_folder:
            return False
        if not self.action:
            return False
        if not self.listitem:
            return False
        if not self.dummy.success:
            return False
        return True

    """
    Action
    """

    def execute_action(self):
        kodi_log(['lib.player - executing action:\n', self.action], 1)
        # Kodi launches busy dialog on home screen that needs to be told to close
        # Otherwise the busy dialog will prevent window activation for folder path
        executebuiltin('Dialog.Close(busydialog, force)')
        executebuiltin(self.action)

    @property
    def on_action(self):
        if not self.path:
            return False
        if not self.is_folder:
            return False
        if not self.action:
            return False
        if not self.dummy.success:
            return False
        return True

    """
    Execute
    """

    @cached_property
    def dummy(self):
        from tmdbhelper.lib.player.action.dummy import PlayerDummy
        return PlayerDummy(self)

    @cached_property
    def success(self):
        return self.execute()

    def execute(self):

        if self.on_action:
            self.execute_action()
            return True

        if self.on_player:
            self.execute_player()
            return True

        if self.on_seturl:
            self.execute_seturl()
            return True

        return False


class PlayerResolverNone(PlayerResolverBase):
    action_type = PLAYER_ACTION_TYPE_NONE
    path_folder = None
    is_resolved = False

    @cached_property
    def is_strm(self):
        if self.player.is_strm:
            return True
        return bool(self.path.endswith('.strm'))

    @cached_property
    def is_folder(self):
        if not self.path:
            return
        if self.path.startswith('executebuiltin://'):
            return True
        if self.path_folder is not None:
            return self.path_folder
        return self.player.is_folder

    @cached_property
    def action(self):
        if not self.path:
            return
        if self.path.startswith('executebuiltin://'):
            return self.path.replace('executebuiltin://', '')
        if self.is_folder:
            return format_folderpath(self.path)
        if not self.player.is_resolvable:
            return self.path

    @cached_property
    def listitem(self):
        self.player.item.details.params = {}
        self.player.item.details.path = self.path
        self.player.item.details.infoproperties['isPlayable'] = 'false' if self.is_folder else 'true'
        self.player.item.details.infoproperties['is_folder'] = 'true' if self.is_folder else 'false'
        return self.player.item.details.get_listitem()

    @cached_property
    def next_episodes_list(self):
        if not self.player.make_playlist:
            return
        return self.next_episodes.listitems

    @cached_property
    def next_episodes(self):
        from tmdbhelper.lib.player.action.episodes import PlayerNextEpisodes
        return PlayerNextEpisodes(
            tmdb_id=self.player.item.tmdb_id,
            season=self.player.item.season,
            episode=self.player.item.episode,
            player=self.player.file
        )


class PlayerResolverList(PlayerResolverNone):
    action_type = PLAYER_ACTION_TYPE_LIST

    @cached_property
    def path_finder(self):
        from tmdbhelper.lib.player.action.pathfinder import PathFinder
        return PathFinder(self.player.item.string_format_map, self.player.actions)

    @cached_property
    def path(self):
        try:
            return self.path_finder.path_tuple[0]
        except (AttributeError, IndexError, TypeError):
            return

    @cached_property
    def path_folder(self):
        try:
            return self.path_finder.path_tuple[1]
        except (AttributeError, IndexError, TypeError):
            return


class PlayerResolverFStr(PlayerResolverNone):
    action_type = PLAYER_ACTION_TYPE_FSTR

    @cached_property
    def path(self):
        if self.player.is_local:
            return self.player.actions
        return self.player.item.string_format_map(self.player.actions)


def PlayerResolver(player, handle=None):
    if isinstance(player.actions, list):
        return PlayerResolverList(player, handle=handle)
    if isinstance(player.actions, str):
        return PlayerResolverFStr(player, handle=handle)
