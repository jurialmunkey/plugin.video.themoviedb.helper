from tmdbhelper.lib.monitor.itemdetails import MonitorItemDetails
from tmdbhelper.lib.monitor.basegetter import BaseItemInfoGetter


class ListItemInfoGetter(BaseItemInfoGetter):

    # ==========
    # PROPERTIES
    # ==========

    def get_cur_item(self):
        return self._item.get_identifier()

    def get_cur_info(self):
        """
        Check to see if some form of information is retrievable from item
        Previously checked only folderpath but might be problematic for static items without one
        Now check to see if there is a label or icon first
        """
        return (
            self._item.get_infolabel('label')
            or self._item.get_infolabel('icon')
            or self._item.get_infolabel('folderpath')
            or self._item.get_infolabel('filenameandpath')
            or self._item.get_infolabel('path')
        )

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

    def is_same_base_window(self, update=True):
        self.cur_base_window = self.get_cur_base_window()
        if self.cur_base_window == self.pre_base_window:
            return self.cur_base_window
        if update:
            self.pre_base_window = self.cur_base_window

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
