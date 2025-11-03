from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_setting
from tmdbhelper.lib.addon.logger import kodi_log


class PlayerDummy:

    filename = 'dummy.mp4'
    listitem_path = f'{ADDONPATH}/resources/dummy.mp4'

    def __init__(self, resolver=None):
        self.resolver = resolver

    def wait(self, fileext=None, timeout=5, suspend=0):
        from tmdbhelper.lib.player.action.waiting import PlayerWaiting
        return PlayerWaiting(
            fileext=fileext,
            timeout=timeout,
            suspend=suspend
        ).run()

    def wait_busy(self):
        from tmdbhelper.lib.player.action.waiting import PlayerWaiting
        PlayerWaiting().wait_busy(self.delay)

    @cached_property
    def delay(self):
        from jurialmunkey.parser import try_float
        return try_float(get_setting('dummy_delay', 'str')) or 1.0

    @cached_property
    def listitem(self):
        from tmdbhelper.lib.items.listitem import ListItem
        return ListItem(path=self.listitem_path).get_listitem()

    @cached_property
    def resolved(self):
        from xbmcplugin import setResolvedUrl
        kodi_log(['lib.player - resolving dummy path to url\n', self.listitem_path], 1)
        setResolvedUrl(self.resolver.handle, True, self.listitem)
        return True

    @cached_property
    def duration(self):
        from jurialmunkey.parser import try_float
        return try_float(get_setting('dummy_duration', 'str')) or 1.0

    @cached_property
    def is_strm(self):
        return self.check_strm()

    def check_strm(self):
        if not self.resolver.is_strm and get_setting('only_resolve_strm'):
            kodi_log(['lib.player - skipped dummy no strm setting\n', self.filename], 1)
            return False
        return True

    @cached_property
    def is_handle(self):
        return self.check_handle()

    def check_handle(self):
        if self.resolver.handle is None:
            kodi_log(['lib.player - skipped dummy no resolve handle\n', self.filename], 1)
            return False
        return True

    @cached_property
    def is_action(self):
        return self.check_action()

    def check_action(self):
        if not self.resolver.is_folder and not self.resolver.action:
            kodi_log(['lib.player - skipped dummy have resolvable file\n', self.filename], 1)
            return False
        return True

    @cached_property
    def is_start(self):
        return self.check_start()

    def check_start(self):
        # Wait till our dummy file plays and then stop after setting duration
        if not self.resolved or not self.wait(fileext=self.filename, suspend=self.duration):
            kodi_log(['lib.player - resolve dummy file timeout\n', self.filename], 1)
            return False
        return True

    @cached_property
    def is_stop(self):
        return self.check_stop()

    def check_stop(self):
        # Wait for our file to stop before continuing
        if self.duration and not self.wait():
            kodi_log(['lib.player - stopped dummy file timeout\n', self.filename], 1)
            return False
        return True

    @cached_property
    def is_done(self):
        return self.check_done()

    def check_done(self):
        # Wait for additional delay after stopping
        self.wait_busy()
        kodi_log(['lib.player - successfully resolved dummy file\n', self.filename], 1)
        return True

    @cached_property
    def success(self):
        return all(func() for func in (
            lambda: self.is_handle,
            lambda: self.is_action,
            lambda: self.is_strm,
            lambda: self.is_start,
            lambda: self.is_stop,
            lambda: self.is_done,
        ))
