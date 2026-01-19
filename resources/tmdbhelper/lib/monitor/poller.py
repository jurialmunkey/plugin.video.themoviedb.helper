from tmdbhelper.lib.addon.plugin import get_condvisibility, get_infolabel
from jurialmunkey.window import WindowChecker

POLL_MIN_INCREMENT = 0.2
POLL_MID_INCREMENT = 1
POLL_MAX_INCREMENT = 2


CV_DISABLED = "!Skin.HasSetting(TMDbHelper.Service)"

WINDOW_PROPERTY_MODAL = ("ServicePause")
WINDOW_XML_MODAL = (
    "DialogSelect.xml",
    "DialogKeyboard.xml",
    "DialogNumeric.xml",
    "DialogConfirm.xml",
    "DialogSettings.xml",
    "DialogMediaSource.xml",
    "DialogTextViewer.xml",
    "DialogSlider.xml",
    "DialogSubtitles.xml",
    "DialogFavourites.xml",
    "DialogColorPicker.xml",
    "DialogBusy.xml",
    "DialogButtonMenu.xml",
    "FileBrowser.xml",
)


WINDOW_XML_MEDIA = (
    'MyVideoNav.xml',
    'MyMusicNav.xml',
    'MyPrograms.xml',
    'MyPics.xml',
    'MyPlaylist.xml',
    'MyGames.xml',
    'MyPVRChannels.xml',
    'MyPVRGuide.xml',
    'MyPVRRecordings.xml',
    'MyPVRSearch.xml',
    'MyPVRTimers.xml'
)

WINDOW_XML_INFODIALOG = (
    'DialogVideoInfo.xml',
    'DialogMusicInfo.xml',
    'DialogPVRInfo.xml'
)

CV_USE_LOCAL_CONTAINER = "Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)"
CV_USE_LOCAL_WINDOWIDS = "Skin.String(TMDbHelper.UseLocalWindowIDs)"

CV_SCROLL = "Container.Scrolling"

WINDOW_XML_CONTEXT = (
    "DialogContextMenu.xml",
    "DialogVideoManager.xml",
    "DialogAddonSettings.xml",
    "DialogAddonInfo.xml",
    "DialogPictureInfo.xml",
)

ON_SCREENSAVER = "System.ScreenSaverActive"

ON_FULLSCREEN = "Window.IsVisible(VideoFullScreen.xml)"
WINDOW_XML_FULLSCREEN = ('VideoFullScreen.xml', )


class Poller(WindowChecker):
    _cond_on_disabled = CV_DISABLED
    _cleared_property = False

    def _on_idle(self, wait_time=30):
        self.update_monitor.waitForAbort(wait_time)

    def _on_modal(self):
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_context(self):
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_scroll(self):
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_listitem(self):
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_clear(self):
        self._on_idle(POLL_MID_INCREMENT)

    def _on_exit(self):
        return

    def _on_fullscreen(self):
        self._on_idle(POLL_MAX_INCREMENT)

    localwidgetcontainer_default_window_ids = (
        10000, 11101, 11102, 11103, 11104,
        11105, 11106, 11107, 11108, 11109,
    )

    @property
    def localwidgetcontainer_window_ids(self):
        try:
            values = get_infolabel(CV_USE_LOCAL_WINDOWIDS).split('|')
            values = tuple((int(i) for i in values)) if values else None
            return values or self.localwidgetcontainer_default_window_ids
        except (AttributeError, ValueError, TypeError):
            return self.localwidgetcontainer_default_window_ids

    @property
    def is_on_fullscreen(self):
        if not self.is_current_base_window_xml(WINDOW_XML_FULLSCREEN):
            return False
        if self.is_current_window_xml(WINDOW_XML_INFODIALOG):
            return False
        if self.is_on_localwidgetcontainer:
            return False
        return True

    @property
    def is_on_localwidgetcontainer(self):
        if not get_condvisibility(CV_USE_LOCAL_CONTAINER):
            return False
        if not self.get_window_property('WidgetContainer'):
            return False
        return True

    @property
    def is_on_globalwidgetcontainer(self):
        if get_condvisibility(CV_USE_LOCAL_CONTAINER):
            return False
        if not self.get_window_property('WidgetContainer', is_home=True):
            return False
        return True

    @property
    def is_on_disabled(self):
        return get_condvisibility(self._cond_on_disabled)

    @property
    def is_on_screensaver(self):
        return get_condvisibility(ON_SCREENSAVER)

    @property
    def is_on_modal(self):
        if self.is_current_window_xml(WINDOW_XML_MODAL):
            return True
        if self.get_window_property(WINDOW_PROPERTY_MODAL):
            return True
        return False

    @property
    def is_on_context(self):
        if self.is_current_window_xml(WINDOW_XML_CONTEXT):
            return True
        return False

    @property
    def is_on_scroll(self):
        return get_condvisibility(CV_SCROLL)

    @property
    def is_on_listitem(self):
        if self.is_on_mediawindow:
            return True
        if self.is_on_localwidgetcontainer:
            return True
        if self.is_on_globalwidgetcontainer:
            return True
        return False

    @property
    def is_on_mediawindow(self):
        # Get the current window again just to double check that it hasn't changed in the interim
        self.get_current_window()
        if self.is_current_window_xml(WINDOW_XML_INFODIALOG):
            return True
        if self.is_current_window_xml(WINDOW_XML_MEDIA):
            return True
        return False

    @property
    def is_on_clear(self):
        # Get the current base window again just to double check that it hasn't changed in the interim
        self.get_current_base_window()
        if self.current_base_window in self.localwidgetcontainer_window_ids:
            return False
        if self.is_on_infodialog:
            return False
        if self.is_current_base_window_xml(WINDOW_XML_MEDIA):  # We check base here as we won't clear if underlying window is open
            return False
        return True

    @property
    def is_on_infodialog(self):
        return any((get_condvisibility(f'Window.IsVisible({i})') for i in WINDOW_XML_INFODIALOG))

    def poller(self):
        while not self.update_monitor.abortRequested() and not self.exit:
            self.get_current_base_window()
            self.get_current_window()

            if self.get_window_property('ServiceStop', is_home=True):
                self.exit = True
                break

            # sit idle when on fullscreen video and treat like screensaver
            if self.is_on_fullscreen:
                self._on_fullscreen()
                continue

            # Sit idle in a holding pattern if the skin doesn't need the service monitor yet
            if self.is_on_disabled:
                self._on_clear()
                self._on_idle(5)
                continue

            # Sit idle in a holding pattern if screen saver is active
            if self.is_on_screensaver:
                self._on_idle(POLL_MAX_INCREMENT)
                continue

            # skip when modal or busy dialogs are opened (e.g. select / progress / busy etc.)
            if self.is_on_modal:
                self._on_modal()
                continue

            # manage context menu separately from other modals to pass info through
            if self.is_on_context:
                self._on_context()
                continue

            # skip when container scrolling
            if self.is_on_scroll:
                self._on_scroll()
                continue

            # media window is opened or widgetcontainer set - start listitem monitoring!
            if self.is_on_listitem:
                self._on_listitem()
                continue

            if self.is_on_clear:
                self._on_clear()
                continue

            # Otherwise just sit here and wait a moment
            self._on_idle(POLL_MIN_INCREMENT)  # self._on_clear()  Use to be clear but not sure we should

        # Some clean-up once service exits
        self._on_exit()
