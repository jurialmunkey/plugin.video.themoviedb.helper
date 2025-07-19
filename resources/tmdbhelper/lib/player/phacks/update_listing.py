from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_infolabel, executebuiltin
from jurialmunkey.parser import try_int


class PlayerHacksUpdateListing:
    """
    Some plugins use container.update after search results to rewrite path history
    This is a quick hack to rewrite the path back to our original path before updating
    """

    timeout = 20

    def __init__(self, folder_path=None, reset_focus=None):
        self.folder_path = folder_path or get_infolabel("Container.FolderPath")
        self.reset_focus = reset_focus or self.get_reset_focus_command()

    def get_reset_focus_command(self):
        if self.folder_path:
            containerid = get_infolabel("System.CurrentControlID")
            current_pos = get_infolabel(f'Container({containerid}).CurrentItem')
            return f'SetFocus({containerid},{try_int(current_pos) - 1},absolute)'

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    def executebuiltin_update_path(self):
        executebuiltin(f'Container.Update({self.folder_path},replace)')

    def is_current_folder_path(self):
        return bool(get_infolabel("Container.FolderPath") == self.folder_path)

    def wait_to_reset_focus_poller(self):
        while not self.xbmc_monitor.abortRequested() and not self.is_current_folder_path and self.timeout > 0:
            self.xbmc_monitor.waitForAbort(0.25)
            self.timeout -= 1

    def executebuiltin_reset_focus(self):
        executebuiltin(self.reset_focus)

    def run(self):
        if not self.folder_path:
            return
        self.xbmc_monitor.waitForAbort(2)  # Wait a moment for kodi to update container properly
        if self.is_current_folder_path:
            return
        self.executebuiltin_update_path()  # Reset back to our original path
        if not self.reset_focus:
            return
        self.wait_to_reset_focus_poller()
        self.executebuiltin_reset_focus()
        self.xbmc_monitor.waitForAbort(0.5)  # TODO: Not 100% sure if we need to wait here or not
