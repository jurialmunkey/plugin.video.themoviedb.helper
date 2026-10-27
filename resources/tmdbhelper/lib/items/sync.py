from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.auth import SyncProviderAuthorisation


class SyncPlayData(SyncProviderAuthorisation):
    def __init__(self, pauseplayprogress=False, watchedindicators=False):
        super().__init__('watched')
        self._pauseplayprogress = pauseplayprogress  # Set play progress using paused at position
        self._watchedindicators = watchedindicators  # Set watched status and playcount

    def get_provider(self):
        return self.syncdata.registry.get_selected_provider(self.capability)

    @property
    def is_enabled(self):
        return self._watchedindicators or self._pauseplayprogress

    def is_sync(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_enabled:
                return
            return func(self, *args, **kwargs)
        return wrapper

    @cached_property
    def syncdata(self):
        from tmdbhelper.lib.sync.datasync import SyncDataFactory
        return SyncDataFactory()

    @is_sync
    def pre_sync(self, info=None, tmdb_type=None, **kwargs):
        info_movies = ('stars_in_movies', 'crew_in_movies', 'trakt_userlist', 'stars_in_both', 'crew_in_both',)
        if tmdb_type in ('movie', 'both',) or info in info_movies:
            if self._watchedindicators:
                self.syncdata.sync('movie', ('plays', ))
            if self._pauseplayprogress:
                self.syncdata.sync('movie', ('playback_progress', ))

        info_tvshow = ('stars_in_tvshows', 'crew_in_tvshows', 'trakt_userlist', 'trakt_calendar', 'stars_in_both', 'crew_in_both', 'specified_episodes')
        if tmdb_type in ('tv', 'season', 'both',) or info in info_tvshow:
            if self._watchedindicators:
                self.syncdata.sync('show', ('plays', 'watched_episodes', 'aired_episodes', ))
            if self._pauseplayprogress:
                self.syncdata.sync('show', ('playback_progress', ))

    @is_sync
    def pre_sync_start(self, **kwargs):
        from tmdbhelper.lib.addon.thread import SafeThread
        self._pre_sync = SafeThread(target=self.pre_sync, kwargs=kwargs)
        self._pre_sync.start()

    @is_sync
    def pre_sync_join(self):
        try:
            self._pre_sync.join()
        except AttributeError:
            return
