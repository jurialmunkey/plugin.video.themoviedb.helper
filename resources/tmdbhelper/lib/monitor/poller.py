from tmdbhelper.lib.addon.plugin import get_condvisibility
from jurialmunkey.window import WindowChecker

POLL_MIN_INCREMENT = 0.2
POLL_MID_INCREMENT = 1
POLL_MAX_INCREMENT = 2


CV_DISABLED = (
    "!Skin.HasSetting(TMDbHelper.Service) + "
    "!Skin.HasSetting(TMDbHelper.EnableCrop) + "
    "!Skin.HasSetting(TMDbHelper.EnableBlur) + "
    "!Skin.HasSetting(TMDbHelper.EnableDesaturate) + "
    "!Skin.HasSetting(TMDbHelper.EnableColors)")

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

CV_FULLSCREEN_LISTITEM = ("Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer) + !String.IsEmpty(Window.Property(TMDbHelper.WidgetContainer))")

CV_SCROLL = "Container.Scrolling"

WINDOW_PROPERTY_CONTEXT = ("ContextMenu")
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
        self._on_idle(POLL_MIN_INCREMENT)

    def _on_exit(self):
        return

    def _on_player(self):
        return

    def _on_fullscreen(self):
        self._on_player()
        if self.is_current_window_xml(WINDOW_XML_INFODIALOG) or get_condvisibility(CV_FULLSCREEN_LISTITEM):
            return self._on_listitem()
        self._on_idle(POLL_MID_INCREMENT)

    @property
    def is_on_fullscreen(self):
        return self.is_current_window_xml(WINDOW_XML_FULLSCREEN)

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
        if self.get_window_property(WINDOW_PROPERTY_CONTEXT):
            return True
        return False

    @property
    def is_on_scroll(self):
        return get_condvisibility(CV_SCROLL)

    @property
    def is_on_listitem(self):
        if self.is_current_window_xml(WINDOW_XML_INFODIALOG):
            return True
        if self.is_current_window_xml(WINDOW_XML_MEDIA):
            return True
        if self.get_window_property('WidgetContainer', is_home=True):
            return True
        if self.get_window_property('WidgetContainer'):
            return True
        return False

    def poller(self):
        while not self.update_monitor.abortRequested() and not self.exit:
            self.get_current_window()  # Get the current window ID and store for this loop

            if self.get_window_property('ServiceStop', is_home=True):
                self.exit = True

            # If we're in fullscreen video then we should update the playermonitor time
            elif self.is_on_fullscreen:
                self._on_fullscreen()

            # Sit idle in a holding pattern if the skin doesn't need the service monitor yet
            elif self.is_on_disabled:
                self._on_idle(30)

            # Sit idle in a holding pattern if screen saver is active
            elif self.is_on_screensaver:
                self._on_idle(POLL_MAX_INCREMENT)

            # skip when modal or busy dialogs are opened (e.g. select / progress / busy etc.)
            elif self.is_on_modal:
                self._on_modal()

            # manage context menu separately from other modals to pass info through
            elif self.is_on_context:
                self._on_context()

            # skip when container scrolling
            elif self.is_on_scroll:
                self._on_scroll()

            # media window is opened or widgetcontainer set - start listitem monitoring!
            elif self.is_on_listitem:
                self._on_listitem()

            # Otherwise just sit here and wait
            else:
                self._on_clear()

        # Some clean-up once service exits
        self._on_exit()
