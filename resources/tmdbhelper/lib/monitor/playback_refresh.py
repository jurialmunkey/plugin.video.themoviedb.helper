from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.tmdate import set_timestamp


class PlaybackRefresh:
    def __init__(self, provider, syncdata):
        self.provider = provider
        self.syncdata = syncdata

    def refresh(self, sync=False):
        self.refresh_watched(sync=sync)

    def refresh_watched(self, sync=False):
        provider = self.syncdata.registry.get_selected_provider('watched')
        if provider is None or provider.provider_id != self.provider.provider_id:
            return
        from tmdbhelper.lib.sync.invalidator import SyncInvalidatorWatchedProgress
        invalidator = SyncInvalidatorWatchedProgress()
        invalidator.syncdata = self.syncdata
        invalidator.notification = False
        invalidator.run(sync=sync)
        get_property('Widgets.Reload', set_property=str(set_timestamp(0, True)))


def PlaybackRefreshFactory(provider, syncdata):
    return PlaybackRefresh(provider, syncdata)
