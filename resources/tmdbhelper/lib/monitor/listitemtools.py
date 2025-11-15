import xbmcgui
from tmdbhelper.lib.addon.plugin import get_infolabel, get_condvisibility, get_localized
from tmdbhelper.lib.addon.logger import kodi_try_except
from tmdbhelper.lib.monitor.common import CommonMonitorFunctions
from tmdbhelper.lib.monitor.listitemgetter import ListItemInfoGetter
from tmdbhelper.lib.monitor.listitemfinaliser import ListItemMonitorFinaliserContainerMethod, ListItemMonitorFinaliserWindowMethod
from tmdbhelper.lib.items.listitem import ListItem


class ListItemMonitorFunctions(CommonMonitorFunctions, ListItemInfoGetter):
    def __init__(self, service_monitor=None):
        super(ListItemMonitorFunctions, self).__init__()
        self.cur_item = 0
        self.pre_item = 1
        self.cur_window = 0
        self.pre_window = 1
        self._ignored_labels = ('..', get_localized(33078).lower(), get_localized(209).lower())
        self._listcontainer = None
        self._last_listitem = None
        self.property_prefix = 'ListItem'
        self._pre_artwork_thread = None
        self.service_monitor = service_monitor  # ServiceMonitor
        self.process_thread = []
        self.process_mutex = False

    # ==========
    # PROPERTIES
    # ==========

    @property
    def listcontainer_id(self):
        return int(self.get_monitor_container() or 0)

    @property
    def listcontainer(self):
        return self.get_listcontainer(self.cur_window, self._listcontainer_id)

    # =======
    # GETTERS
    # =======

    def get_listcontainer(self, window_id=None, container_id=None):
        if not window_id or not container_id:
            return
        if not get_condvisibility(f'Control.IsVisible({container_id})'):
            return -1
        return container_id

    # ================
    # SETUP PROPERTIES
    # ================

    def setup_current_container(self):
        """ Cache property getter return values for performance """
        super().setup_current_container()
        self._listcontainer_id = self.listcontainer_id
        self._listcontainer = self.listcontainer

    # =========
    # FUNCTIONS
    # =========

    def add_item_listcontainer(self, listitem, window_id=None, container_id=None):
        try:
            _win = xbmcgui.Window(window_id or self.cur_window)  # Note get _win separate from _lst
            _lst = _win.getControl(container_id or self._listcontainer)  # Note must get _lst in same func as addItem else crash
        except Exception:
            _lst = None
        if not _lst:
            return
        _lst.addItem(listitem)  # Note dont delay adding listitem after retrieving list else memory reference changes
        return listitem

    # =======
    # ACTIONS
    # =======

    def on_finalise(self):
        func = (
            ListItemMonitorFinaliserContainerMethod
            if self._listcontainer else
            ListItemMonitorFinaliserWindowMethod
        )
        func(self).finalise()

    @kodi_try_except('lib.monitor.listitem.on_listitem')
    def on_listitem(self):
        self.setup_current_container()
        self.setup_current_item()

        # We want to set a special container but it doesn't exist so exit
        if self._listcontainer == -1:
            return

        # Check if the item has changed before retrieving details again
        if self.is_same_item(update=True) and self.is_same_window(update=True):
            return

        # Ignore some special folders like next page and parent folder
        if (self.get_infolabel('Label') or '').lower().split(' (', 1)[0] in self._ignored_labels:
            return self.on_exit()

        # Set a property for skins to check if item details are updating
        self.get_property('IsUpdating', 'True')

        # Finish up setting our details to the container/window
        self.on_finalise()

        # Clear property for skins to check if item details are updating
        self.get_property('IsUpdating', clear_property=True)

    @kodi_try_except('lib.monitor.listitem.on_context_listitem')
    def on_context_listitem(self):
        if not self._last_listitem:
            return
        _id_dialog = xbmcgui.getCurrentWindowDialogId()
        _id_d_list = self.get_listcontainer(_id_dialog, self._listcontainer_id)
        if not _id_d_list or _id_d_list == -1:
            return
        _id_window = xbmcgui.getCurrentWindowId()
        _id_w_list = self.get_listcontainer(_id_window, self._listcontainer_id)
        if not _id_w_list or _id_w_list == -1:
            return
        self.add_item_listcontainer(self._last_listitem, _id_dialog, _id_d_list)

    def on_scroll(self):
        return

    def on_exit(self, is_done=True):

        if self._listcontainer:
            self.add_item_listcontainer(ListItem().get_listitem())

        self.clear_properties()

        if is_done:
            self.get_property('IsUpdating', clear_property=True)
