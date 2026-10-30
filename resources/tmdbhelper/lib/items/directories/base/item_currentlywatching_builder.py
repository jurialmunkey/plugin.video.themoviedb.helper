from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type
from tmdbhelper.lib.items.directories.base.item_sync_builder import BaseDirSyncItemBuilder


class BaseDirCurrentlyWatchingItemBuilder(BaseDirSyncItemBuilder):
    @cached_property
    def label_item_type(self):
        return self.get_label_item_type()

    def get_label_item_type(self):
        if not self.mixed_dir:
            return ''
        item_type = 'episode' if self.item_type == 'tv' else self.item_type
        return convert_type(item_type, 'plural')
