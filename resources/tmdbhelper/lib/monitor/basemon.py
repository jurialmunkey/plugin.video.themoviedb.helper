from tmdbhelper.lib.monitor.poller import Poller, POLL_MIN_INCREMENT
from tmdbhelper.lib.monitor.listitemgetter import ListItemInfoGetter
from tmdbhelper.lib.addon.logger import kodi_try_except
from tmdbhelper.lib.addon.thread import SafeThread
from jurialmunkey.window import WindowPropertySetter


class BaseItemMonitor(SafeThread, ListItemInfoGetter, Poller, WindowPropertySetter):
    def __init__(self, parent):
        SafeThread.__init__(self)
        self.cur_item = 0
        self.pre_item = 1
        self.cur_window = 0
        self.pre_window = 1
        self.exit = False
        self.update_monitor = parent.update_monitor
        self._allow_on_scroll = True  # Allow updating while scrolling
        self._parent = parent

    def is_next_refresh(self):
        self.setup_current_item()

        # Always refresh our info if window changed
        if not self.is_same_window(update=True):
            return True

        # Always refresh our info if the item changed
        if not self.is_same_item(update=True):
            return True

        return False

    @kodi_try_except('lib.monitor.basemon.on_listitem')
    def on_listitem(self):
        self.update_baseitem()

    def update_baseitem(self, forced=False):
        if self.get_monitor_container():
            return
        self.setup_current_container()
        if not forced and not self.is_next_refresh():
            return
        for k, v in self.baseitem_properties.items():
            self.get_property(f'ListItem.{k}', set_property=v, clear_property=(v is None))

    def _on_listitem(self):
        self.on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_scroll(self):
        if self._allow_on_scroll:
            return self._on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def run(self):
        self.poller()
