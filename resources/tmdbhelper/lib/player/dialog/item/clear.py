from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.player.dialog.item.basic import PlayerItemBasic
from tmdbhelper.lib.addon.plugin import get_localized


class PlayerItemClearDefault(PlayerItemBasic):

    is_valid = True
    plugin_name = 'plugin.video.themoviedb.helper'

    @cached_property
    def name(self):
        return get_localized(32311)
