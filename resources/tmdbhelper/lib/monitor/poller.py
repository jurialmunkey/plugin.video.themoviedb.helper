from tmdbhelper.lib.addon.plugin import get_condvisibility
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
)

WINDOW_XML_INFODIALOG = (
    'DialogVideoInfo.xml',
    'DialogMusicInfo.xml',
    'DialogPVRInfo.xml',
    'MyPVRChannels.xml',
    'MyPVRGuide.xml'
)

CV_USE_LOCAL_CONTAINER = "Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)"

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

    def _on_clear(self, wait_time):
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_exit(self):
        return

    def _on_fullscreen(self):
        self._on_idle(POLL_MID_INCREMENT)

    @property
    def is_on_fullscreen(self):
        if not self.is_current_window_xml(WINDOW_XML_FULLSCREEN):
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
        self.get_current_window()  # Get the current window again to make sure we can monitor
        if self.is_current_window_xml(WINDOW_XML_INFODIALOG):
            return True
        if self.is_current_window_xml(WINDOW_XML_MEDIA):
            return True
        if self.is_on_localwidgetcontainer:
            return True
        if self.is_on_globalwidgetcontainer:
            return True
        return False

    def poller(self):
        while not self.update_monitor.abortRequested() and not self.exit:
            self.get_current_window()  # Get the current window ID and store for this loop

            if self.get_window_property('ServiceStop', is_home=True):
                self.exit = True
                break

            # If we're in fullscreen video then we should update the playermonitor time
            if self.is_on_fullscreen:
                self._on_fullscreen()
                continue

            # Sit idle in a holding pattern if the skin doesn't need the service monitor yet
            if self.is_on_disabled:
                if not self._cleared_property:
                    self._on_clear()
                    self._cleared_property = True
                self._on_idle(5)
                continue

            # Service restarted so set flag back
            self._cleared_property = False

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

            # Otherwise just sit here and wait a moment
            self._on_idle(POLL_MIN_INCREMENT)  # self._on_clear()  Use to be clear but not sure we should

        # Some clean-up once service exits
        self._on_exit()
