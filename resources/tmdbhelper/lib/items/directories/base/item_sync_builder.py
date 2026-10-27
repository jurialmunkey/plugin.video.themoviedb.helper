from tmdbhelper.lib.items.directories.base.item_builder import BaseDirItemBuilder
from jurialmunkey.ftools import cached_property


class BaseDirSyncItemBuilder(BaseDirItemBuilder):
    @cached_property
    def infoproperties(self):
        return self.get_infoproperties()

    def get_infoproperties(self):
        infoproperties = super().infoproperties
        if self.base_item.sorting:
            infoproperties['is_sortable'] = 'sync'
        return infoproperties
