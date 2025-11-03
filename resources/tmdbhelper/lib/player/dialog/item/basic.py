from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.player.dialog.item.rules import PlayerItemAssertRule


class PlayerItemBasic:

    name = ''
    is_folder = False
    is_provider = 0
    is_resolvable = True
    is_local = False
    is_strm = False
    requires_ids = False
    make_playlist = False
    next_episodes = None
    plugin_name = ''
    plugin_icon = ''
    fallback = ''
    actions = ()
    rules = ()
    item = None
    file = ''
    mode = ''

    @cached_property
    def is_valid(self):
        if not self.actions:
            return False
        if not self.item:  # No item so no need to assert values as we're only building to choose default player
            return True
        if all((PlayerItemAssertRule(self.item, rule).is_valid for rule in self.rules)):
            return True
        return False
