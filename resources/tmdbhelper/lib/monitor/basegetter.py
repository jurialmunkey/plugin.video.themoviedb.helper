from jurialmunkey.ftools import cached_property
from jurialmunkey.window import get_current_window
from tmdbhelper.lib.addon.plugin import get_infolabel, get_condvisibility, get_skindir
import tmdbhelper.lib.monitor.utils as monitor_utils


class BaseItemInfoGetter:

    """
    Basic Details
    """

    @property
    def container_content(self):
        return get_infolabel('Container.Content()')

    @cached_property
    def cur_window(self):
        return self.get_cur_window()

    def get_cur_window(self):
        return get_current_window()

    @cached_property
    def widget_id(self):
        return self.get_widget_id()

    def get_widget_id(self):
        return monitor_utils.widget_id(self.cur_window)

    @cached_property
    def container(self):
        return self.get_container()

    def get_container(self):
        return monitor_utils.container(self.widget_id)

    @cached_property
    def container_item(self):
        return self.get_container_item()

    def get_container_item(self):
        return monitor_utils.container_item(self.container)

    def get_infolabel(self, info, position=0):
        return get_infolabel(f'{self.container_item.format(position)}{info}')

    def get_condvisibility(self, info, position=0):
        return get_condvisibility(f'{self.container_item.format(position)}{info}')

    @staticmethod
    def get_monitor_container():
        return get_infolabel('Skin.String(TMDbHelper.MonitorContainer)')

    """
    BaseItem
    """

    @cached_property
    def baseitem_skindefaults(self):
        from tmdbhelper.lib.monitor.baseitem import BaseItemSkinDefaults
        return BaseItemSkinDefaults()

    @property
    def baseitem_properties(self):
        infoproperties = {}
        for k, v, func in self.baseitem_skindefaults[get_skindir()]:
            if func == 'boolean':
                infoproperties[k] = 'True' if all([self.get_condvisibility(i) for i in v]) else None
                continue
            try:
                value = next(j for j in (self.get_infolabel(i) for i in v) if j)
                value = func(value) if func else value
                infoproperties[k] = value
            except StopIteration:
                infoproperties[k] = None
        return infoproperties
