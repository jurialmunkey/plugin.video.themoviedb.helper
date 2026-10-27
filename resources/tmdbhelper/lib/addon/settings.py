from time import monotonic
from xbmc import Monitor
from xbmcgui import ControlButton, Window
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDON, executebuiltin, get_condvisibility, get_localized
from tmdbhelper.lib.addon.logger import kodi_log


class AddonSettingsDialog:
    """Reopen addon settings at a category/button specified by localization IDs.

    Call reopen() after an action launched by a settings control with
    <close>true</close>, normally in the caller's finally block.
    """

    def __init__(self, category_label, setting_label):
        self.category_label = category_label
        self.setting_label = setting_label

    @cached_property
    def window(self):
        return Window(10140)

    def get_button_id(self, label, controls):
        # Control.GetLabel masks negative IDs; read the native button's primary label.
        for control_id in controls:
            try:
                control = self.window.getControl(control_id)
            except RuntimeError as exc:
                if str(exc) == 'Unknown control type for python':
                    continue  # Kodi's spin/slider variants cannot be wrapped by Python.
                if str(exc) == f'Non-Existent Control {control_id}':
                    return  # Dynamic controls are contiguous, or not yet created.
                raise
            if isinstance(control, ControlButton) and control.getLabel() == label:
                return control_id

    def focus_control(self, control_id):
        if self.window.getFocusId() == control_id:
            return True
        # setFocusId queues a GUI message. Confirm it on a later iteration.
        self.window.setFocusId(control_id)
        return False

    def is_ready(self, addon_id):
        return (
            get_condvisibility('Window.IsActive(addonsettings)')
            and get_condvisibility('Window.IsDialogTopmost(addonsettings)')
            and self.window.getProperty('Addon.ID') == addon_id
        )

    def is_settled(self, addon_id):
        if not self.is_ready(addon_id):
            self.ready_at = None
            return False
        if self.ready_at is None:
            self.ready_at = monotonic()
        # Active becomes true before the opening animation has settled.
        return monotonic() - self.ready_at >= 1.0

    def focus_label(self, label, controls):
        if self.pending_control_id is None:
            self.pending_control_id = self.get_button_id(get_localized(label), controls)
        if self.pending_control_id is None:
            return False
        if not self.focus_control(self.pending_control_id):
            return False
        self.pending_control_id = None
        return True

    def restore_focus(self, addon_id):
        if not self.is_settled(addon_id):
            return False
        if self.category_focused:
            return self.focus_label(self.setting_label, range(-180, 0))
        self.category_focused = self.focus_label(self.category_label, range(-200, -180))
        return False

    def reopen(self):
        addon_id = ADDON.getAddonInfo('id')
        executebuiltin(f'Addon.OpenSettings({addon_id})')
        monitor = Monitor()
        self.ready_at = None
        self.category_focused = False
        self.pending_control_id = None
        for _ in range(100):
            if self.restore_focus(addon_id):
                return
            if monitor.waitForAbort(0.05):
                return
        kodi_log(f'{self.__class__.__name__}: timed out restoring the settings position', 2)
