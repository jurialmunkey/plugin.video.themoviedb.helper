from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import KeyGetter
from tmdbhelper.lib.addon.plugin import get_localized, get_setting


class ResolverItem:
    def __init__(self, data):
        self.data = data
        self.meta = KeyGetter(data)

    @cached_property
    def episode(self):
        return self.meta.get_key('episode')

    @cached_property
    def title(self):
        return self.meta.get_key('title')

    @cached_property
    def name(self):
        return self.meta.get_key('name')

    @cached_property
    def year(self):
        return self.meta.get_key('year')

    @cached_property
    def header(self):
        header = self.name or get_localized(32042)
        header = f'{header} - {self.title}' if self.episode and self.title else header
        return header


class ResolverPlayer:

    def __init__(self, data):
        self.data = data
        self.meta = KeyGetter(data)

    @cached_property
    def requires_ids(self):
        return self.meta.get_key('requires_ids')

    @cached_property
    def idx(self):
        return self.meta.get_key('idx')

    @cached_property
    def file(self):
        return self.meta.get_key('file')

    @cached_property
    def mode(self):
        return self.meta.get_key('mode')

    @cached_property
    def name(self):
        return self.meta.get_key('name')

    @cached_property
    def fallback(self):
        return self.meta.get_key('fallback')

    @cached_property
    def make_playlist(self):
        return self.meta.get_key('make_playlist')

    @cached_property
    def is_resolvable(self):
        return self.meta.get_key('is_resolvable')

    @cached_property
    def plugin_name(self):
        return self.meta.get_key('plugin_name')

    @cached_property
    def is_local(self):
        return self.meta.get_key('is_local')

    @cached_property
    def item(self):
        return {
            'is_local': 'true' if self.is_local else 'false',
            'is_resolvable': 'true' if self.is_resolvable else 'false',
            'player_name': self.name
        }


class ResolverPlayerSelect:

    fallback_item_func = None

    def __init__(self, meta, dialog_players=None, action_log=None):
        self.meta = ResolverItem(meta)
        self.dialog_players = dialog_players
        self.action_log = action_log

    def del_player(self):
        del self.dialog_players[self.player.idx]  # Avoid reasking for failed player

    @property
    def url(self):
        return self.resolved_path[0]

    @property
    def is_folder(self):
        return self.resolved_path[1]

    def on_success(self):
        self.action_log += ('SUCCESS!', '\n')
        item = {
            'url': self.url,
            'is_folder': 'true' if self.is_folder else 'false',
            'isPlayable': 'false' if self.is_folder else 'true',
        }
        item.update(self.player.item)
        return item

    def on_failure(self):
        self.action_log += ('FAILURE!', '\n')
        self.del_player() if self.player.idx is not None else None
        self.player = ResolverPlayer(player) if (player := self.get_fallback_item()) is not None else self.get_player()
        return self.get_resolved_path() if self.player else None

    def get_fallback_item(self):
        return self.fallback_item_func(self.player.fallback) if self.player.fallback else None

    def resolved_path_func(self, player=None):
        """ Returns tuple of (path, is_folder) """
        if not player or not isinstance(player, dict):
            return

        actions = player.get('actions')

        if not actions:
            return

        if isinstance(actions, list):
            from tmdbhelper.lib.player.actions.pathfinder import PathFinder
            return PathFinder(self.string_format_func, actions).path_tuple

        if isinstance(actions, str):
            if not player.get('is_local', False):
                actions = self.string_format_func(actions)  # Format our path if a single path and not a file
            return (actions, player.get('is_folder', False))

    @cached_property
    def resolved_path(self):
        return self.get_resolved_path()

    def get_resolved_path(self):
        self.action_log += (
            'PLAYER: ', self.player.file, ' ', self.player.mode, ' ', self.player.is_resolvable, '\n',
            'PLUGIN: ', self.player.plugin_name, '\n')
        path = self.resolved_path_func(self.player.data)
        return path if path and isinstance(path, tuple) else self.on_failure()

    @cached_property
    def select_player_class(self):
        from tmdbhelper.lib.player.select import PlayerSelectStandard, PlayerSelectCombined
        return PlayerSelectCombined if get_setting('combined_players') else PlayerSelectStandard

    def select_player(self, header=None, detailed=True):
        """ Returns user selected player via dialog - detailed bool switches dialog style """
        instance = self.select_player_class(players=self.dialog_players)
        return instance.select(header=header, detailed=detailed)

    def update_player(self, player):
        setattr(self, 'player', ResolverPlayer(player)) if player else None

    @cached_property
    def player(self):
        return self.get_player()

    def get_player(self):
        player = self.select_player(header=self.meta.header)
        return ResolverPlayer(player) if player else None

    @cached_property
    def item(self):
        return self.on_success() if self.resolved_path else None
