from tmdbhelper.lib.monitor.images import ImageManipulations
from tmdbhelper.lib.monitor.poller import Poller, POLL_MIN_INCREMENT
from tmdbhelper.lib.monitor.listitemtools import ListItemInfoGetter
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.addon.logger import kodi_try_except
from tmdbhelper.lib.addon.thread import SafeThread


class ImagesMonitor(SafeThread, ListItemInfoGetter, ImageManipulations, Poller):
    _cond_on_disabled = (
        "!Skin.HasSetting(TMDbHelper.EnableCrop) + "
        "!Skin.HasSetting(TMDbHelper.EnableBlur) + "
        "!Skin.HasSetting(TMDbHelper.EnableDesaturate) + "
        "!Skin.HasSetting(TMDbHelper.EnableColors)")

    _allow_list = ('crop', 'blur', 'desaturate', 'colors', )
    _check_list = (
        'Art(fanart)', 'Art(poster)', 'Art(clearlogo)',
        'Art(tvshow.fanart)', 'Art(tvshow.poster)', 'Art(tvshow.clearlogo)',
        'Art(artist.fanart)', 'Art(artist.poster)', 'Art(artist.clearlogo)',
        'Art(thumb)', 'Art(icon)',
    )
    _dbtype_refresh = ('', None, 'addon', 'file', 'genre', 'country', 'studio', 'year', 'tag', 'director')
    _next_refresh_increment = 10  # Reupdate idle item every ten seconds for extrafanart TODO: Allow skin to set value?
    _this_refresh_increment = 3   # How long to wait for ListItem.Art() availability check

    def __init__(self, parent):
        SafeThread.__init__(self)
        self._cur_item = 0
        self._pre_item = 1
        self._cur_window = 0
        self._pre_window = 1
        self._next_refresh = 0
        self._this_refresh = 0
        self.exit = False
        self.update_monitor = parent.update_monitor
        self.crop_image_cur = None
        self.blur_image_cur = None
        self.remote_artwork = {}
        self._allow_on_scroll = True  # Allow updating while scrolling
        self._parent = parent

    def is_this_refresh(self):
        # Some dbtypes are unlikely to have artwork so refresh immediately to clear
        if self.get_infolabel('dbtype') in self._dbtype_refresh:
            return True

        # There is sometimes a delay in Kodi loading Art() dictionary so check we can get it before refreshing
        if next((j for j in (self.get_infolabel(i) for i in self._check_list) if j), None):
            return True

        if not self._this_refresh:
            self._this_refresh = set_timestamp(self._this_refresh_increment)
            return False

        # Refresh time expired and were still on same item so refresh anyway
        if not get_timestamp(self._this_refresh):
            return True

        return False

    def is_next_refresh(self):
        # Always refresh our artwork if window changed
        if not self.is_same_window(update=True):
            return True

        # Always refresh our artwork if the item changed
        if not self.is_same_item(update=True):
            return True

        # Set refresh time if not set yet and still on same item
        if not self._next_refresh:
            self._next_refresh = set_timestamp(self._next_refresh_increment)
            return False

        # Refresh time expired and were still on same item so refresh for extrafanart cycling
        if not get_timestamp(self._next_refresh):
            return True

        return False

    @kodi_try_except('lib.monitor.imgmon.on_listitem')
    def on_listitem(self):
        with self._parent.mutex_lock:
            self.update_artwork()

    def update_artwork(self):
        self.setup_current_container()
        if not self.is_this_refresh():
            return
        if not self.is_next_refresh():
            return
        self._this_refresh = 0
        self._next_refresh = 0
        self.get_image_manipulations(
            use_winprops=True,
            built_artwork=self.remote_artwork.get(self._pre_item),
            allow_list=self._allow_list)

    def _on_listitem(self):
        self.on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_scroll(self):
        if self._allow_on_scroll:
            return self._on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def run(self):
        self.poller()
