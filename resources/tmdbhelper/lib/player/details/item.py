from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import KeyGetter, get_localized, ADDONPATH
from xbmcaddon import Addon as KodiAddon


class PlayerItemAssertRule:
    def __init__(self, item, rule):
        self.item = item  # Item details
        self.rule = rule  # Player assert rules

    @cached_property
    def inverted(self):
        return self.rule.startswith('!')

    @cached_property
    def key(self):
        return self.rule[1:] if self.inverted else self.rule

    @cached_property
    def value(self):
        return self.item.get(self.key)

    @cached_property
    def condition(self):
        return bool(self.value and self.value != 'None')

    @cached_property
    def is_valid(self):
        return bool(not self.condition) if self.inverted else self.condition


class PlayerItemConstructed:

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
        return self.mode not in self.play_modes

    @cached_property
    def is_provider(self):
        if self.is_folder:
            return False
        return self.meta_get('is_provider')

    @cached_property
    def is_resolvable(self):
        return self.meta_get('is_resolvable')

    @cached_property
    def requires_ids(self):
        return self.meta_get('requires_ids') or False

    @cached_property
    def make_playlist(self):
        return self.meta_get('make_playlist')

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
    def fallback_split(self):
        return self.fallback.split() if self.fallback else None

    @cached_property
    def fallback_file(self):
        return self.fallback_split[0] if self.fallback_split else None

    @cached_property
    def fallback_mode(self):
        return self.fallback_split[1] if self.fallback_split else None

    @cached_property
    def actions(self):
        return self.meta_get(self.mode)

    @cached_property
    def configured_item(self):
        if not self.is_valid:
            return
        return {
            'file': self.file,
            'mode': self.mode,
            'is_folder': self.is_folder,
            'is_provider': self.is_provider,
            'is_resolvable': self.is_resolvable,
            'requires_ids': self.requires_ids,
            'make_playlist': self.make_playlist,
            'name': self.name,
            'plugin_name': self.plugin_name,
            'plugin_icon': self.plugin_icon,
            'fallback': self.fallback,
            'actions': self.actions,
        }

    @cached_property
    def rules(self):
        rules = self.meta
        rules = KeyGetter(rules).get_key('assert')
        rules = KeyGetter(rules).get_key(self.mode) or []
        return rules

    @cached_property
    def is_valid(self):
        if not self.actions:
            return False
        if not self.item:  # No item so no need to assert values as we're only building to choose default player
            return True
        if all((PlayerItemAssertRule(self.item, rule).is_valid for rule in self.rules)):
            return True
        return False
