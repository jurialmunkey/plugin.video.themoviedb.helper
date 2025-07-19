from tmdbhelper.lib.items.directories.base.item_builder import BaseDirItemBuilder
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, get_localized
from jurialmunkey.ftools import cached_property


class BaseDirItem:
    priority = 999
    label_localized = 0
    label_type = 'standard'
    label_prefix = ''
    label_append = ''
    label_suffix = ''
    types = ()
    params = {}
    path = PLUGINPATH
    sorting = False
    filters = False
    infoproperties = {}
    infolabels = {}

    item_builder = BaseDirItemBuilder

    art_landscape = 'fanart.jpg'
    art_icon = 'resources/icons/themoviedb/default.png'

    @cached_property
    def label(self):
        return {
            'localize': '{label_localized}',
            'standard': '{label_localized}{{space}}{{item_type}}',
            'reversed': '{{item_type}}{{space}}{label_localized}',
            'prefixed': '{label_prefix} {label_localized}',
            'appended': '{label_localized}{{space}}{{item_type}} ({label_append})',
            'suffixed': '{label_localized} {label_suffix}',
        }[self.label_type].format(
            label_localized=get_localized(self.label_localized),
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def art(self):
        return {
            'landscape': f'{ADDONPATH}/{self.art_landscape}',
            'icon': f'{ADDONPATH}/{self.art_icon}'
        }

    def get_item(self, item_type, mixed_dir=False):
        return self.item_builder(self, item_type, mixed_dir).item
