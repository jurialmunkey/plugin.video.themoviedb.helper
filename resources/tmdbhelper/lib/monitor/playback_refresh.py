from jurialmunkey.window import get_property
from tmdbhelper.lib.addon.tmdate import set_timestamp


class PlaybackRefresh:
    def __init__(self, provider, syncdata):
        self.provider = provider
        self.syncdata = syncdata

    def refresh(self, history_changed, sync=False):
        provider = self.syncdata.registry.get_selected_provider('watched')
        if provider is None or provider.provider_id != self.provider.provider_id:
            return
        from tmdbhelper.lib.sync.invalidator import SyncInvalidatorWatchedProgress
        invalidator = SyncInvalidatorWatchedProgress()
        invalidator.syncdata = self.syncdata
        invalidator.notification = False
        invalidator.run(sync=sync)
        get_property('Widgets.Reload', set_property=str(set_timestamp(0, True)))


class TraktPlaybackRefresh(PlaybackRefresh):
    def __init__(self, provider, syncdata, trakt_api):
        super().__init__(provider, syncdata)
        self.trakt_api = trakt_api

    def refresh(self, history_changed, sync=False):
        super().refresh(history_changed, sync=sync)
        if history_changed:
            from tmdbhelper.lib.script.method.trakt import get_stats
            get_stats(trakt_api=self.trakt_api, forced=True)


def PlaybackRefreshFactory(provider, syncdata):
    if provider.provider_id == 'trakt':
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktPlaybackRefresh(provider, syncdata, TraktAPI())
    return PlaybackRefresh(provider, syncdata)
