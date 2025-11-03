from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import boolean
from tmdbhelper.lib.addon.plugin import KeyGetter, get_localized, ADDONPATH
from tmdbhelper.lib.player.dialog.item.basic import PlayerItemBasic
from xbmcaddon import Addon as KodiAddon


class PlayerItemConstructed(PlayerItemBasic):

    play_modes = ('play_movie', 'play_episode')

    def __init__(self, item, mode, meta, file):
        self.item = item  # Item details
        self.mode = mode  # Player mode e.g. play_movie
        self.meta = meta  # Player details
        self.file = file  # Player filename

    @cached_property
    def meta_getter(self):
        return KeyGetter(self.meta)

    def meta_get(self, key):
        return self.meta_getter.get_key(key)

    @cached_property
    def name_prefix(self):
        if self.mode in self.play_modes:
            return get_localized(32061)
        return get_localized(137)

    @cached_property
    def name(self):
        name = self.meta_get('name')
        return f'{self.name_prefix} {name}'

    @cached_property
    def is_folder(self):
        return bool(self.mode not in self.play_modes)

    @cached_property
    def is_provider(self):
        if self.is_folder:
            return False
        return boolean(self.meta_get('is_provider'))

    @cached_property
    def is_resolvable(self):
        return boolean(self.meta_get('is_resolvable'))

    @cached_property
    def requires_ids(self):
        return boolean(self.meta_get('requires_ids'))

    @cached_property
    def make_playlist(self):
        if self.mode != 'play_episode':
            return False
        return boolean(self.meta_get('make_playlist'))

    @cached_property
    def plugin_name(self):
        return self.meta_get('plugin') or ''

    @cached_property
    def plugin_icon(self):
        plugin_icon = self.meta_get('icon')
        plugin_icon = plugin_icon or KodiAddon(self.plugin_name).getAddonInfo('icon') or ''
        plugin_icon = plugin_icon.format(ADDONPATH)
        return plugin_icon

    @cached_property
    def fallback(self):
        return KeyGetter(self.meta_get('fallback')).get_key(self.mode)

    @cached_property
    def actions(self):
        return self.meta_get(self.mode)

    @cached_property
    def rules(self):
        rules = self.meta
        rules = KeyGetter(rules).get_key('assert')
        rules = KeyGetter(rules).get_key(self.mode) or []
        return rules
