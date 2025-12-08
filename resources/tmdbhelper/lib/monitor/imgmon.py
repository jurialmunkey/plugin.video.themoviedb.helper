from tmdbhelper.lib.monitor.images import ImageManipulations
from tmdbhelper.lib.monitor.poller import Poller, POLL_MIN_INCREMENT
from tmdbhelper.lib.monitor.listitemgetter import ListItemInfoGetter
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
        self.cur_item = 0
        self.pre_item = 1
        self.cur_window = 0
        self.pre_window = 1
        self.cur_base_window = 0
        self.pre_base_window = 1
        self._next_refresh = 0
        self._this_refresh = 0
        self.exit = False
        self.update_monitor = parent.update_monitor
        self.crop_image_cur = None
        self.blur_image_cur = None
        self.remote_artwork = {}
        self._allow_on_scroll = True  # Allow updating while scrolling
        self._parent = parent

    # Unused method see update_artwork comments further below
    """
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
    """

    def is_next_refresh(self):

        # Check we can actually get something from underlying item
        if self.is_same_base_window(update=True) and not self.get_cur_info():
            return False

        # Check if the item has changed before retrieving details again
        if not self.is_same_item(update=True) or not self.is_same_window(update=True):
            return True

        # Set refresh time if not set yet and still on same item
        if not self._next_refresh:
            self._next_refresh = set_timestamp(self._next_refresh_increment)
            return False

        # Check refresh time and refresh if it has expired
        if not get_timestamp(self._next_refresh):
            return True

        return False

    @kodi_try_except('lib.monitor.imgmon.on_listitem')
    def on_listitem(self):
        with self._parent.mutex_lock:
            self.update_artwork()

    def update_artwork(self, forced=False):
        self.setup_current_container()
        self.setup_current_item()

        # Unused method is_this_refresh for checking if listitem.art() is ready as Kodi delays adding until after directory loads listitems
        # Causes more problems that it is worth to try to check so we skip this method and live with art occassionally being online instead of local
        # FIXME: Possible alternative would be to only check once after window or folderpath change
        """
        if not self.is_this_refresh():
            return
        """

        if not forced and not self.is_next_refresh():
            return

        self._this_refresh = 0
        self._next_refresh = 0

        update_artwork = self.get_image_manipulations(
            use_winprops=False,
            built_artwork=self.remote_artwork.get(self.pre_item),
            allow_list=self._allow_list
        )

        if not self.update_properties(update_artwork):
            return

        if not self.update_properties(self.baseitem_properties):
            return

        return update_artwork

    def update_properties(self, infoproperties):
        if not self.is_same_item():
            return False
        for k, v in infoproperties.items():
            self.get_property(f'ListItem.{k}', set_property=v, clear_property=(v is None))
        return True

    def _on_listitem(self):
        self.on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_scroll(self):
        if self._allow_on_scroll:
            return self._on_listitem()
        self._on_idle(POLL_MIN_INCREMENT)

    def run(self):
        self.poller()
