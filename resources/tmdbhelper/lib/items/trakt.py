from tmdbhelper.lib.files.ftools import cached_property


class TraktPlayData():
    def __init__(self, pauseplayprogress=False, watchedindicators=False, unwatchedepisodes=False):
        self._pauseplayprogress = pauseplayprogress  # Set play progress using paused at position
        self._watchedindicators = watchedindicators  # Set watched status and playcount
        self._unwatchedepisodes = unwatchedepisodes  # Set unwatched episode count to total episode count for unwatched tvshows (if false)

    def is_sync(func):
        def wrapper(self, *args, **kwargs):
            if not self.trakt_syncdata:
                return
            return func(self, *args, **kwargs)
        return wrapper

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        api = TraktAPI()
        api.attempted_login = True  # Avoid asking for authorization
        return api

    @cached_property
    def trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    @is_sync
    def pre_sync(self, info=None, tmdb_type=None, **kwargs):
        info_movies = ('stars_in_movies', 'crew_in_movies', 'trakt_userlist', 'stars_in_both', 'crew_in_both',)
        if tmdb_type in ('movie', 'both',) or info in info_movies:
            if self._watchedindicators:
                self.trakt_syncdata.sync('movie', ('plays', ))
            if self._pauseplayprogress:
                self.trakt_syncdata.sync('movie', ('playback_progress', ))

        info_tvshow = ('stars_in_tvshows', 'crew_in_tvshows', 'trakt_userlist', 'trakt_calendar', 'stars_in_both', 'crew_in_both',)
        if tmdb_type in ('tv', 'season', 'both',) or info in info_tvshow:
            if self._watchedindicators:
                self.trakt_syncdata.sync('show', ('plays', 'watched_episodes', 'aired_episodes', ))
            if self._pauseplayprogress:
                self.trakt_syncdata.sync('show', ('playback_progress', ))

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
