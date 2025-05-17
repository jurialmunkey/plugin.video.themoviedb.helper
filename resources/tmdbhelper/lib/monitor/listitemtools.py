import xbmcgui
from tmdbhelper.lib.addon.plugin import get_infolabel, get_condvisibility, get_localized, get_skindir
from tmdbhelper.lib.addon.logger import kodi_try_except
from jurialmunkey.window import get_property, get_current_window
from tmdbhelper.lib.monitor.common import CommonMonitorFunctions
from tmdbhelper.lib.monitor.itemdetails import MonitorItemDetails
from tmdbhelper.lib.monitor.baseitem import BaseItemSkinDefaults
from tmdbhelper.lib.items.listitem import ListItem
from tmdbhelper.lib.addon.thread import SafeThread

CV_USE_LISTITEM = (
    "!Skin.HasSetting(TMDbHelper.ForceWidgetContainer) + "
    "!Window.IsActive(script-tmdbhelper-recommendations.xml) + ["
    "!Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer) | String.IsEmpty(Window.Property(TMDbHelper.WidgetContainer))] + ["
    "Window.IsVisible(movieinformation) | "
    "Window.IsVisible(musicinformation) | "
    "Window.IsVisible(songinformation) | "
    "Window.IsVisible(addoninformation) | "
    "Window.IsVisible(pvrguideinfo) | "
    "Window.IsVisible(tvchannels) | "
    "Window.IsVisible(tvguide)]")

CV_USE_LOCAL_CONTAINER = "Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)"


class ListItemInfoGetter():
    def get_infolabel(self, info, position=0):
        return get_infolabel(f'{self._container_item.format(position)}{info}')

    def get_condvisibility(self, info, position=0):
        return get_condvisibility(f'{self._container_item.format(position)}{info}')

    def get_item_identifier(self, position=0):
        return str((
            'current_listitem_v5.1.17',
            self.get_infolabel('dbtype', position),
            self.get_infolabel('dbid', position),
            self.get_infolabel('IMDBNumber', position),
            self.get_infolabel('title', position) or self.get_infolabel('label', position),
            self.get_infolabel('tvshowtitle', position),
            self.get_infolabel('year', position),
            self.get_infolabel('season', position),
            self.get_infolabel('episode', position),))

    # ==========
    # PROPERTIES
    # ==========

    @property
    def cur_item(self):
        return self.get_item_identifier()

    @property
    def cur_window(self):
        return get_current_window()

    @property  # CHANGED _cur_window
    def widget_id(self):
        window_id = self._cur_window if get_condvisibility(CV_USE_LOCAL_CONTAINER) else None
        return get_property('WidgetContainer', window_id=window_id, is_type=int)

    @property  # CHANGED _widget_id and assign
    def container(self):
        return f'Container({self._widget_id}).' if self._widget_id else 'Container.'

    @property  # CHANGED _container
    def container_item(self):
        return 'ListItem.' if get_condvisibility(CV_USE_LISTITEM) else f'{self._container}ListItem({{}}).'

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


class ListItemMonitorFunctions(CommonMonitorFunctions, ListItemInfoGetter):
    def __init__(self, parent):
        super(ListItemMonitorFunctions, self).__init__()
        self._cur_item = 0
        self._pre_item = 1
        self._cur_window = 0
        self._pre_window = 1
        self._ignored_labels = ['..', get_localized(33078).lower(), get_localized(209).lower()]
        self._listcontainer = None
        self._last_listitem = None
        self._item = None
        self.property_prefix = 'ListItem'
        self._pre_artwork_thread = None
        self._baseitem_skindefaults = BaseItemSkinDefaults()
        self._parent = parent

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

    def setup_current_item(self):
        self._item = MonitorItemDetails(self, position=0)

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

    def on_finalise_listcontainer(self, process_artwork=True, process_ratings=True):
        """ Constructs ListItem adds to hidden container
        process_artwork=True: Optional bool to process artwork
        process_ratings=True: Optional bool to process ratings
        Processing of artwork and ratings is done in a background thread to avoid locking main loop
        """
        _item = self._item
        _item.set_additional_properties(self.baseitem_properties)
        _listitem = self._last_listitem = _item.listitem
        _pre_item = self._pre_item
        _detailed = {'artwork': None, 'ratings': None}

        if _pre_item != self.cur_item:
            return

        self.add_item_listcontainer(_listitem)

        def _process_artwork():
            _artwork = _item.artwork
            _artwork.update(_item.get_image_manipulations(built_artwork=_artwork, use_winprops=True))
            _detailed['artwork'] = _artwork

        def _process_ratings():
            _ratings = _item.all_ratings
            _detailed['ratings'] = _ratings

        def _process_artwork_ratings():
            self.get_property('IsUpdatingRatings', 'True')

            # Thread ratings and artwork processing
            t_artwork = SafeThread(target=_process_artwork) if process_artwork else None
            t_ratings = SafeThread(target=_process_ratings) if process_ratings else None
            t_artwork.start() if t_artwork else None
            t_ratings.start() if t_ratings else None

            # Wait for threads to join before readding listitem
            t_artwork.join() if t_artwork else None
            t_ratings.join() if t_ratings else None

            self.get_property('IsUpdatingRatings', clear_property=True)

            # Check focused item is still the same before updating
            if _pre_item != self.cur_item:
                return

            self._parent.images_monitor._pre_item = _pre_item

            _listitem.setArt(_detailed['artwork'] or {}) if process_artwork else None
            _listitem.setProperties(_detailed['ratings'] or {}) if process_ratings else None

        if process_artwork or process_ratings:
            t = SafeThread(target=_process_artwork_ratings)
            t.start()

    def on_finalise_winproperties(self, process_artwork=True, process_ratings=True):
        _item = self._item
        _item.set_additional_properties(self.baseitem_properties)
        _pre_item = self._pre_item

        if _pre_item != self.cur_item:
            return

        def process_ratings():
            ratings_item = {'ratings': _item.all_ratings}

            if _pre_item != self.cur_item:
                return

            with self._parent.mutex_lock:
                self.set_ratings_properties(ratings_item)

        def process_ratings_thread():
            self.get_property('IsUpdatingRatings', 'True')
            process_ratings()
            self.get_property('IsUpdatingRatings', clear_property=True)

        # Process ratings in thread to avoid holding up main loop
        if process_ratings:
            t = SafeThread(target=process_ratings_thread)
            t.start()

        with self._parent.mutex_lock:
            # Add remote artwork to artwork monitor and update in case local items doesn't have some artwork types
            if process_artwork and _item.artwork:
                self._parent.images_monitor.remote_artwork[_pre_item] = _item.artwork.copy()
                self._parent.images_monitor.update_artwork(forced=True)

            # Set the main properties
            self.set_properties(_item.item)

    def on_finalise(self):
        func = self.on_finalise_listcontainer if self._listcontainer else self.on_finalise_winproperties
        func(
            process_artwork=get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableArtwork)"),
            process_ratings=get_condvisibility("!Skin.HasSetting(TMDbHelper.DisableRatings)"))
        self.get_property('IsUpdating', clear_property=True)

    @kodi_try_except('lib.monitor.listitem.on_listitem')
    def on_listitem(self):
        self.setup_current_container()

        # We want to set a special container but it doesn't exist so exit
        if self._listcontainer == -1:
            return

        # Check if the item has changed before retrieving details again
        if self.is_same_window(update=True) and self.is_same_item(update=True):
            return

        # Ignore some special folders like next page and parent folder
        if (self.get_infolabel('Label') or '').lower().split(' (', 1)[0] in self._ignored_labels:
            return self.on_exit()

        # Set a property for skins to check if item details are updating
        self.get_property('IsUpdating', 'True')

        # Get the current listitem details for the details lookup
        self.setup_current_item()

        # Finish up setting our details to the container/window
        self.on_finalise()

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
