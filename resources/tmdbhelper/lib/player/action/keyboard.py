
from xbmc import Monitor
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
from tmdbhelper.lib.addon.plugin import get_condvisibility
from tmdbhelper.lib.addon.thread import SafeThread


class KeyboardInputter(SafeThread):
    def __init__(self, action=None, text=None, timeout=300):
        SafeThread.__init__(self)
        self.text = text
        self.action = action
        self.exit = False
        self.poll = 0.5
        self.timeout = timeout

    def poller(self):
        if self.text and get_condvisibility("Window.IsVisible(DialogKeyboard.xml)"):
            get_jsonrpc("Input.SendText", {"text": self.text, "done": True})
            self.exit = True
            return

        if self.action and get_condvisibility("Window.IsVisible(DialogSelect.xml) | Window.IsVisible(DialogConfirm.xml)"):
            get_jsonrpc(self.action)
            self.exit = True
            return

    @cached_property
    def xbmc_monitor(self):
        return Monitor()

    @property
    def loop_condition(self):
        if self.xbmc_monitor.abortRequested():
            return False
        if self.exit:
            return False
        if self.timeout <= 0:
            return False
        return True

    def run(self):
        while self.loop_condition:
            self.xbmc_monitor.waitForAbort(self.poll)
            self.timeout -= self.poll
            self.poller()
