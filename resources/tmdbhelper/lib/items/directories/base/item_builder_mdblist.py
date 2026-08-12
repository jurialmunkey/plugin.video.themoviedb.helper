from tmdbhelper.lib.items.directories.base.item_builder import BaseDirItemBuilder
from tmdbhelper.lib.addon.consts import RUNSCRIPT
from jurialmunkey.ftools import cached_property


class BaseDirItemMDbListBuilder(BaseDirItemBuilder):
    @cached_property
    def context_menu(self):
        if not self.base_item.sorting:
            return []
        return [(
            self.base_item.sort_label,
            RUNSCRIPT.format('sort_mdblist,{}'.format(','.join(f'{k}={v}' for k, v in self.params.items())))
        )]

    @cached_property
    def infoproperties(self):
        infoproperties = super().infoproperties
        infoproperties['is_sortable'] = 'mdblist' if self.base_item.sorting else None
        return infoproperties
