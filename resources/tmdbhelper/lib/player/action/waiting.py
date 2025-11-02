from jurialmunkey.ftools import cached_property


class PlayerWaiting:

    def __init__(self, fileext=None, timeout=5, polling=0.25, suspend=0):
        self.fileext = fileext  # File extension (or full filename) we wait to start (if None/False we wait for player to stop and if True we wait for anyfile)
        self.timeout = timeout  # How long to wait before giving up
        self.polling = polling  # Increments to check status
        self.suspend = suspend  # Suspend for this time before stopping

    @cached_property
    def xbmc_monitor(self):
        from xbmc import Monitor
        return Monitor()

    @cached_property
    def xbmc_player(self):
        from xbmc import Player
        return Player()

    @property
    def is_playing(self):
        return self.xbmc_player.isPlaying()

    @property
    def playing_file(self):
        return self.xbmc_player.getPlayingFile()

    @cached_property
    def is_fileext_str(self):
        return isinstance(self.fileext, str)

    @property
    def wait_condition(self):
        if not self.fileext:
            return bool(self.is_playing)
        if not self.is_playing:
            return True
        if not self.is_fileext_str:
            return False
        if not self.playing_file.endswith(self.fileext):
            return True
        return False

    def wait_busy(self, time):
        from tmdbhelper.lib.addon.dialog import BusyDialog
        with BusyDialog(False if time < 1 else True):
            self.xbmc_monitor.waitForAbort(time)

    def run(self):
        poll = 0
        while (
                not self.xbmc_monitor.abortRequested()
                and self.timeout > poll
                and self.wait_condition
        ):
            self.xbmc_monitor.waitForAbort(self.polling)
            poll += self.polling

        if self.timeout <= poll:
            return False
        if not self.fileext:
            return True
        if not self.suspend:
            return True

        self.xbmc_monitor.waitForAbort(self.suspend)

        if not self.is_playing:
            return True
        if not self.playing_file.endswith(self.fileext):
            return True

        self.xbmc_player.stop()
        return True
