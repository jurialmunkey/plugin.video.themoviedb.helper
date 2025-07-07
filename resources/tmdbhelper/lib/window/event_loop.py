from xbmcgui import Window
import jurialmunkey.window as window
from tmdbhelper.lib.addon.plugin import executebuiltin, get_condvisibility
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.window.direct_call_auto import DirectCallAutoInfoDialog
from tmdbhelper.lib.window.constants import (
    ID_VIDEOINFO,
    PREFIX_INSTANCE,
    PREFIX_ADDPATH,
    PREFIX_PATH,
    CONTAINER_ID,
    PREFIX_COMMAND
)


class EventLoop():
    def _call_exit(self, return_info=False):
        self.return_info = return_info
        self.exit = True

    def _on_exit(self):
        # Clear our properties
        self.reset_properties()

        # Close video info dialog
        if window.is_visible(ID_VIDEOINFO):
            window.close(ID_VIDEOINFO)
            window.wait_until_active(ID_VIDEOINFO, invert=True, poll=0.1)

        # Close base window
        if window.is_visible(self.window_id):
            executebuiltin('Action(Back)')
            window.wait_until_active(self.window_id, invert=True, poll=0.1)

    def _on_add(self):
        self.position += 1
        self.set_properties(self.position, window.get_property(PREFIX_ADDPATH))
        window.wait_for_property(PREFIX_ADDPATH, None, True, poll=0.3)  # Clear property before continuing

    def _on_rem(self):
        self.position -= 1
        name = f'{PREFIX_PATH}{self.position}'
        self.set_properties(self.position, window.get_property(name))

    def _on_back(self):
        name = f'{PREFIX_PATH}{self.position}'
        window.wait_for_property(name, None, True, poll=0.3)
        return self._on_rem() if self.position > 1 else self._call_exit(True)

    def _on_change_window(self, poll=0.3):
        # Close the info dialog first before doing anything
        if window.is_visible(ID_VIDEOINFO):
            window.close(ID_VIDEOINFO)

            # If we timeout or user forced back out of base window then we exit
            if not window.wait_until_active(ID_VIDEOINFO, self.base_id, poll=poll, invert=True):
                return False

        # NOTE: Used to check for self.position == 0 and exit here
        # Now checking prior to routine
        if not self.first_run:
            return True

        # On first run we need to open the base window
        window.activate(self.window_id)
        if window.wait_until_active(self.window_id, poll=poll):
            return True

        # Window ID didnt open successfully
        return False

    def _on_change_manual(self):
        # Close the info dialog and open base window first before doing anything
        if not self._on_change_window():
            return False

        # Check that base window has correct control ID and clear it out
        control_list = Window(self.kodi_id).getControl(CONTAINER_ID)
        if not control_list:
            kodi_log(f'SKIN ERROR!\nControl {CONTAINER_ID} unavailable in Window {self.window_id}', 1)
            return False
        control_list.reset()

        # Wait for the container to update before doing anything
        if not window.wait_until_updated(container_id=CONTAINER_ID, instance_id=self.window_id):
            return False

        # Open the info dialog
        Window(self.kodi_id).setFocus(control_list)
        executebuiltin(f'SetFocus({CONTAINER_ID},0,absolute)')
        executebuiltin('Action(Info)')
        if not window.wait_until_active(ID_VIDEOINFO, self.window_id):
            return False

        return True

    def _on_change_direct(self):
        direct = DirectCallAutoInfoDialog(self.added_path)

        # Check we can get a listitem
        if not direct.listitem:
            return False

        # Close the info dialog and open base window before continuing
        if not self._on_change_window(poll=0.1):
            return False

        # Open the info dialog
        direct.open()

        if not window.wait_until_active(ID_VIDEOINFO, self.window_id, poll=0.5):
            return False

        return True

    @cached_property
    def on_change_method(self):
        if get_condvisibility("Skin.HasSetting(TMDbHelper.DirectCallAuto)"):
            return self._on_change_direct
        return self._on_change_manual

    def _on_change(self):
        # On last position let's exit
        if self.position == 0:
            return self._call_exit(True)

        # Update item and info dialog or exit if failed
        if not self.on_change_method():
            return self._call_exit()

        # Set current_path to added_path because we've now updated everything
        # Set first_run to False because we've now finished our first run through
        self.current_path = self.added_path
        self.first_run = False

    def event_loop_action(self):
        # Path added so let's put it in the queue
        if window.get_property(PREFIX_ADDPATH):
            self._on_add()
            return

        # Exit called so let's exit
        if window.get_property(PREFIX_COMMAND) == 'exit':
            self._call_exit()
            return

        # Path changed so let's update
        if self.current_path != self.added_path:
            self._on_change()
            self.xbmc_monitor.waitForAbort(0.3)
            return

        # User force quit so let's exit
        if not window.is_visible(self.window_id):
            self._call_exit()
            return

        # User pressed back and closed video info window
        if not window.is_visible(ID_VIDEOINFO):
            self._on_back()
            self.xbmc_monitor.waitForAbort(0.3)
            return

        # Nothing happened this round so let's loop and wait
        self.xbmc_monitor.waitForAbort(0.3)

    def event_poll(self):
        if not self.exit and not self.xbmc_monitor.abortRequested():
            self.event_loop_action()
            return self.event_poll()
        return self._on_exit()

    def event_loop(self):
        window.wait_for_property(PREFIX_INSTANCE, 'True', True, poll=0.3)
        self.event_poll()
        window.get_property(PREFIX_INSTANCE, clear_property=True)
