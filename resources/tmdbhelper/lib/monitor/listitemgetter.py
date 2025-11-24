from tmdbhelper.lib.monitor.itemdetails import MonitorItemDetails
from tmdbhelper.lib.monitor.basegetter import BaseItemInfoGetter


class ListItemInfoGetter(BaseItemInfoGetter):

    # ==========
    # PROPERTIES
    # ==========

    def get_cur_item(self):
        return self._item.get_identifier()

    # ==================
    # COMPARISON METHODS
    # ==================

    def is_same_item(self, update=False):
        self.cur_item = self.get_cur_item()
        if self.cur_item == self.pre_item:
            return self.cur_item
        if update:
            self.pre_item = self.cur_item

    def is_same_window(self, update=True):
        self.cur_window = self.get_cur_window()
        if self.cur_window == self.pre_window:
            return self.cur_window
        if update:
            self.pre_window = self.cur_window

    # ================
    # SETUP PROPERTIES
    # ================

    def setup_current_container(self):
        """ Cache property getter return values for performance """
        self.cur_window = self.get_cur_window()
        self.widget_id = self.get_widget_id()
        self.container = self.get_container()
        self.container_item = self.get_container_item()

    def setup_current_item(self):
        self._item = MonitorItemDetails(self, position=0)
