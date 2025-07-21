import xbmcgui
import tmdbhelper.lib.monitor.utils as monitor_utils
from tmdbhelper.lib.addon.plugin import get_infolabel, get_condvisibility, get_localized, get_skindir
from tmdbhelper.lib.addon.logger import kodi_try_except
from jurialmunkey.window import get_current_window
from tmdbhelper.lib.monitor.common import CommonMonitorFunctions
from tmdbhelper.lib.monitor.itemdetails import MonitorItemDetails
from tmdbhelper.lib.monitor.baseitem import BaseItemSkinDefaults
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.thread import SafeThread


class ListItemInfoGetter():
    def get_infolabel(self, info, position=0):
        return get_infolabel(f'{self._container_item.format(position)}{info}')

    def get_condvisibility(self, info, position=0):
        return get_condvisibility(f'{self._container_item.format(position)}{info}')

    # ==========
    # PROPERTIES
    # ==========

    @property
    def cur_item(self):
        return self._item.get_identifier()

    @property
    def cur_window(self):
        return get_current_window()

    @property  # CHANGED _cur_window
    def widget_id(self):
        return monitor_utils.widget_id(self._cur_window)

    @property  # CHANGED _widget_id and assign
    def container(self):
        return monitor_utils.container(self._widget_id)

    @property  # CHANGED _container
    def container_item(self):
        return monitor_utils.container_item(self._container)

    @property
    def container_content(self):
        return get_infolabel('Container.Content()')

    # ==================
    # COMPARISON METHODS
    # ==================

    def is_same_item(self, update=False):
        self._cur_item = self.cur_item
        if self._cur_item == self._pre_item:
            return self._cur_item
        if update:
            self._pre_item = self._cur_item

    def is_same_window(self, update=True):
        self._cur_window = self.cur_window
        if self._cur_window == self._pre_window:
            return self._cur_window
        if update:
            self._pre_window = self._cur_window

    # ================
    # SETUP PROPERTIES
    # ================

    def setup_current_container(self):
        """ Cache property getter return values for performance """
        self._cur_window = self.cur_window
        self._widget_id = self.widget_id
        self._container = self.container
        self._container_item = self.container_item

    def setup_current_item(self):
        self._item = MonitorItemDetails(self, position=0)


class ListItemMonitorFinaliser:
    def __init__(self, listitem_monitor_functions):
        self.listitem_monitor_functions = listitem_monitor_functions  # ListItemMonitorFunctions

    @cached_property
    def ratings_enabled(self):
        return get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableRatings)")

    @cached_property
    def artwork_enabled(self):
        return get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableArtwork)")

    @cached_property
    def processed_artwork(self):
        return {}

    @property
    def baseitem_properties(self):
        return self.listitem_monitor_functions.baseitem_properties

    @property
    def get_property(self):
        return self.listitem_monitor_functions.get_property

    @property
    def set_properties(self):
        return self.listitem_monitor_functions.set_properties

    @property
    def set_ratings_properties(self):
        return self.listitem_monitor_functions.set_ratings_properties

    @property
    def add_item_listcontainer(self):
        return self.listitem_monitor_functions.add_item_listcontainer

    @property
    def service_monitor(self):
        return self.listitem_monitor_functions.service_monitor

    @property
    def mutex_lock(self):
        return self.service_monitor.mutex_lock

    @property
    def images_monitor(self):
        return self.service_monitor.images_monitor

    def ratings(self):
        if not self.item.is_same_item:
            return
        self.set_ratings()

    def artwork(self):
        self.images_monitor.remote_artwork[self.item.identifier] = self.item.artwork.copy()
        self.processed_artwork = self.images_monitor.update_artwork(forced=True) or {}

    def process_artwork(self):
        self.get_property('IsUpdatingArtwork', 'True')
        self.artwork()
        self.get_property('IsUpdatingArtwork', clear_property=True)

    def process_ratings(self):
        self.get_property('IsUpdatingRatings', 'True')
        self.ratings()
        self.get_property('IsUpdatingRatings', clear_property=True)

    def start_process_artwork(self):
        if not self.artwork_enabled:
            return
        if not self.item.artwork:
            return
        with self.mutex_lock:  # Lock to avoid race with artwork monitor
            self.process_artwork()

    def start_process_ratings(self):
        if not self.ratings_enabled:
            return
        self.process_thread.append(SafeThread(target=self.process_ratings))
        if self.process_mutex:  # Already have one thread running a loop to clear out the queue
            return
        self.aquire_process_thread()

    def aquire_process_thread(self):
        self.process_mutex = True
        try:
            process_thread = self.process_thread.pop(0)
        except IndexError:
            self.process_mutex = False
            return
        process_thread.start()
        process_thread.join()
        return self.aquire_process_thread()

    @property
    def process_thread(self):
        return self.listitem_monitor_functions.process_thread

    @property
    def process_mutex(self):
        return self.listitem_monitor_functions.process_mutex

    @process_mutex.setter
    def process_mutex(self, value):
        self.listitem_monitor_functions.process_mutex = value

    @cached_property
    def item(self):
        item = self.listitem_monitor_functions._item
        item.set_additional_properties(self.baseitem_properties)
        return item

    @cached_property
    def listitem(self):
        listitem = self.listitem_monitor_functions._last_listitem = self.item.listitem
        return listitem

    def finalise(self):
        # Initial checks for item
        if not self.initial_checks():
            return

        # Set artwork to monitor as priority
        self.start_process_artwork()

        # Process ratings in thread to avoid holding up main loop
        t = SafeThread(target=self.start_process_ratings)
        t.start()

        # Set some basic details next
        self.start_process_default()


class ListItemMonitorFinaliserContainerMethod(ListItemMonitorFinaliser):

    def start_process_default(self):
        with self.mutex_lock:
            self.listitem.setArt(self.processed_artwork)
            self.add_item_listcontainer(self.listitem)  # Add item to container

    def set_ratings(self):
        ratings = self.item.all_ratings
        with self.mutex_lock:
            self.listitem.setProperties(ratings)

    def initial_checks(self):
        if not self.item:
            return False
        if not self.listitem:
            return False
        if not self.item.is_same_item:  # Check that we are still on the same item after building
            return False
        return True


class ListItemMonitorFinaliserWindowMethod(ListItemMonitorFinaliser):

    def start_process_default(self):
        self.set_properties(self.item.item)

    def set_ratings(self):
        self.set_ratings_properties({'ratings': self.item.all_ratings})

    def initial_checks(self):
        if not self.item:
            return False
        if not self.item.is_same_item:
            return False
        return True


class ListItemMonitorFunctions(CommonMonitorFunctions, ListItemInfoGetter):
    def __init__(self, service_monitor=None):
        super(ListItemMonitorFunctions, self).__init__()
        self._cur_item = 0
        self._pre_item = 1
        self._cur_window = 0
        self._pre_window = 1
        self._ignored_labels = ('..', get_localized(33078).lower(), get_localized(209).lower())
        self._listcontainer = None
        self._last_listitem = None
        self.property_prefix = 'ListItem'
        self._pre_artwork_thread = None
        self._baseitem_skindefaults = BaseItemSkinDefaults()
        self.service_monitor = service_monitor  # ServiceMonitor
        self.process_thread = []
        self.process_mutex = False

    # ==========
    # PROPERTIES
    # ==========

    @property
    def listcontainer_id(self):
        return int(get_infolabel('Skin.String(TMDbHelper.MonitorContainer)') or 0)

    @property
    def listcontainer(self):
        return self.get_listcontainer(self._cur_window, self._listcontainer_id)

    @property
    def baseitem_properties(self):
        infoproperties = {}
        for k, v, func in self._baseitem_skindefaults[get_skindir()]:
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
            _win = xbmcgui.Window(window_id or self._cur_window)  # Note get _win separate from _lst
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
