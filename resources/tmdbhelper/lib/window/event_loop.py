from xbmcgui import Window
import jurialmunkey.window as window
from tmdbhelper.lib.addon.plugin import executebuiltin, get_condvisibility
from tmdbhelper.lib.addon.logger import kodi_log
from jurialmunkey.ftools import cached_property
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
        kodi_log(f'Window Manager [EVENTS] _call_exit return_info:{return_info}', 2)
        self.return_info = return_info
        self.exit = True

    def _on_exit(self):
        kodi_log(f'Window Manager [EVENTS] _on_exit', 2)
        # Clear our properties
        self.reset_properties()

        # Close video info dialog
        if window.is_visible(ID_VIDEOINFO):
            kodi_log(f'Window Manager [EVENTS] _on_exit window.close(ID_VIDEOINFO) [ ]', 2)
            window.close(ID_VIDEOINFO)
            window.wait_until_active(ID_VIDEOINFO, invert=True, poll=0.1)
            kodi_log(f'Window Manager [EVENTS] _on_exit window.close(ID_VIDEOINFO) [X]', 2)

        # Close base window
        if window.is_visible(self.window_id):
            kodi_log(f'Window Manager [EVENTS] _on_exit Action(Back) [ ]', 2)
            executebuiltin('Action(Back)')
            window.wait_until_active(self.window_id, invert=True, poll=0.1)
            kodi_log(f'Window Manager [EVENTS] _on_exit Action(Back) [X]', 2)

    def _on_add(self):
        kodi_log(f'Window Manager [EVENTS] _on_add [ ]', 2)
        self.position += 1
        self.set_properties(self.position, window.get_property(PREFIX_ADDPATH))
        window.wait_for_property(PREFIX_ADDPATH, None, True, poll=0.3)  # Clear property before continuing
        kodi_log(f'Window Manager [EVENTS] _on_add [X]', 2)

    def _on_rem(self):
        kodi_log(f'Window Manager [EVENTS] _on_rem [ ]', 2)
        self.position -= 1
        name = f'{PREFIX_PATH}{self.position}'
        self.set_properties(self.position, window.get_property(name))
        kodi_log(f'Window Manager [EVENTS] _on_rem [X]', 2)

    def _on_back(self):
        kodi_log(f'Window Manager [EVENTS] _on_back [ ]', 2)
        name = f'{PREFIX_PATH}{self.position}'
        window.wait_for_property(name, None, True, poll=0.3)
        kodi_log(f'Window Manager [EVENTS] _on_back [X]', 2)
        return self._on_rem() if self.position > 1 else self._call_exit(True)

    def _on_change_window(self, poll=0.3):
        kodi_log(f'Window Manager [EVENTS] _on_change_window', 2)
        # Close the info dialog first before doing anything
        if window.is_visible(ID_VIDEOINFO):
            kodi_log(f'Window Manager [EVENTS] _on_change_window window.close(ID_VIDEOINFO)', 2)
            window.close(ID_VIDEOINFO)

            # If we timeout or user forced back out of base window then we exit
            if not window.wait_until_active(ID_VIDEOINFO, self.base_id, poll=poll, invert=True):
                kodi_log(f'Window Manager [EVENTS] _on_change_window window.close(ID_VIDEOINFO) FORCED', 2)
                return False

        # NOTE: Used to check for self.position == 0 and exit here
        # Now checking prior to routine
        if not self.first_run:
            kodi_log(f'Window Manager [EVENTS] _on_change_window first_run', 2)
            return True

        # On first run we need to open the base window
        kodi_log(f'Window Manager [EVENTS] _on_change_window activate_base [ ]', 2)
        window.activate(self.window_id)
        if window.wait_until_active(self.window_id, poll=poll):
            kodi_log(f'Window Manager [EVENTS] _on_change_window activate_base [X]', 2)
            return True

        kodi_log(f'Window Manager [EVENTS] _on_change_window activate_base FAILED!', 2)
        # Window ID didnt open successfully
        return False

    def _on_change_manual(self):
        # Close the info dialog and open base window first before doing anything
        if not self._on_change_window():
            return False

        # Check that base window has correct control ID and clear it out
        _window = Window(self.kodi_id)
        control_list = _window.getControl(CONTAINER_ID)
        if not control_list:
            kodi_log(f'SKIN ERROR!\nControl {CONTAINER_ID} unavailable in Window {self.window_id}', 1)
            return False
        control_list.reset()

        # Wait for the container to update before doing anything
        if not window.wait_until_updated(container_id=CONTAINER_ID, instance_id=self.window_id):
            return False

        # Open the info dialog
        _window = Window(self.kodi_id)
        _window.setFocus(control_list)
        executebuiltin(f'SetFocus({CONTAINER_ID},0,absolute)')
        executebuiltin('Action(Info)')
        if not window.wait_until_active(ID_VIDEOINFO, self.window_id):
            return False

        return True

    def _on_change_direct(self):
        kodi_log(f'Window Manager [EVENTS] _on_change_direct', 2)
        direct = DirectCallAutoInfoDialog(self.added_path)

        # Check we can get a listitem
        if not direct.listitem:
            kodi_log(f'Window Manager [EVENTS] _on_change_direct NO LISTITEM!', 2)
            return False

        # Close the info dialog and open base window before continuing
        if not self._on_change_window(poll=0.1):
            kodi_log(f'Window Manager [EVENTS] _on_change_direct window_change FAILED!', 2)
            return False

        # Open the info dialog
        kodi_log(f'Window Manager [EVENTS] _on_change_direct direct.open() [ ]', 2)
        direct.open()
        kodi_log(f'Window Manager [EVENTS] _on_change_direct direct.open() [X]', 2)

        if not window.wait_until_active(ID_VIDEOINFO, self.window_id, poll=0.5):
            kodi_log(f'Window Manager [EVENTS] _on_change_direct direct.open() TIMEOUT!', 2)
            return False

        kodi_log(f'Window Manager [EVENTS] _on_change_direct direct.open() DONE!', 2)
        return True

    @cached_property
    def on_change_method(self):
        if get_condvisibility("Skin.HasSetting(TMDbHelper.DirectCallAuto)"):
            return self._on_change_direct
        return self._on_change_manual

    def _on_change(self):
        kodi_log(f'Window Manager [EVENTS] _on_change', 2)

        # On last position let's exit
        if self.position == 0:
            kodi_log(f'Window Manager [EVENTS] _on_change last_position', 2)
            return self._call_exit(True)

        # Update item and info dialog or exit if failed
        if not self.on_change_method():
            kodi_log(f'Window Manager [EVENTS] _on_change _on_change_method FAILED!', 2)
            return self._call_exit()

        # Set current_path to added_path because we've now updated everything
        # Set first_run to False because we've now finished our first run through
        self.current_path = self.added_path
        self.first_run = False

    def event_poll(self):
        while not self.exit and not self.xbmc_monitor.abortRequested():
            # Path added so let's put it in the queue
            if window.get_property(PREFIX_ADDPATH):
                self._on_add()
                continue

            # Exit called so let's exit
            if window.get_property(PREFIX_COMMAND) == 'exit':
                self._call_exit()
                break

            # Path changed so let's update
            if self.current_path != self.added_path:
                self._on_change()
                continue

            # User force quit so let's exit
            if not window.is_visible(self.window_id):
                self._call_exit()
                break

            # User pressed back and closed video info window
            if not window.is_visible(ID_VIDEOINFO):
                self._on_back()
                continue

            # Nothing happened this round so let's loop and wait
            self.xbmc_monitor.waitForAbort(0.3)

        return self._on_exit()

    def event_loop(self):
        kodi_log(f'Window Manager [EVENTS] _event_loop BEGIN', 2)
        window.wait_for_property(PREFIX_INSTANCE, 'True', True, poll=0.3)
        self.event_poll()
        window.get_property(PREFIX_INSTANCE, clear_property=True)
        kodi_log(f'Window Manager [EVENTS] _event_loop ENDED', 2)
