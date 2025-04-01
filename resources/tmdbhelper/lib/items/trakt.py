class TraktMethods():
    def __init__(self, pauseplayprogress=False, watchedindicators=False, unwatchedepisodes=False):
        self._pauseplayprogress = pauseplayprogress  # Set play progress using paused at position
        self._watchedindicators = watchedindicators  # Set watched status and playcount
        self._unwatchedepisodes = unwatchedepisodes  # Set unwatched episode count to total episode count for unwatched tvshows (if false)

    @property
    def trakt_api(self):
        try:
            return self._trakt_api
        except AttributeError:
            from tmdbhelper.lib.api.trakt.api import TraktAPI
            self._trakt_api = TraktAPI()
            self._trakt_api.attempted_login = True  # Avoid asking for authorization
            return self._trakt_api

    @property
    def trakt_syncdata(self):
        try:
            return self._trakt_syncdata
        except AttributeError:
            self._trakt_syncdata = self.trakt_api.trakt_syncdata
            return self._trakt_syncdata

    def pre_sync(self, info=None, tmdb_id=None, tmdb_type=None, season=None, **kwargs):
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
            if self._pauseplayprogress and tmdb_id is not None and season is not None:
                self.trakt_syncdata.sync('show', ('playback_progress', ))

    def pre_sync_start(self, **kwargs):
        from tmdbhelper.lib.addon.thread import SafeThread
        self._pre_sync = SafeThread(target=self.pre_sync, kwargs=kwargs)
        self._pre_sync.start()

    def pre_sync_join(self):
        try:
            self._pre_sync.join()
        except AttributeError:
            return

    def set_playprogress(self, li):

        def _set_playprogress():
            if li.infolabels.get('mediatype') == 'movie':
                return self.trakt_syncdata.get_movie_playprogress(
                    tmdb_id=li.unique_ids.get('tmdb'))

            return self.trakt_syncdata.get_episode_playprogress(
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                season=li.infolabels.get('season'),
                episode=li.infolabels.get('episode'))

        if not self._pauseplayprogress:
            return

        if li.infolabels.get('mediatype') not in ['movie', 'episode']:
            return

        duration = li.infolabels.get('duration')
        if not duration:
            return

        progress = _set_playprogress()
        if not progress or progress < 4 or progress > 96:
            progress = 0

        li.infoproperties['ResumeTime'] = int(duration * progress // 100)
        li.infoproperties['TotalTime'] = int(duration)

    def get_playcount(self, li):
        if not self._watchedindicators:
            return

        if li.infolabels.get('mediatype') == 'movie':
            return self.trakt_syncdata.get_movie_playcount(
                tmdb_id=li.unique_ids.get('tmdb')) or 0

        if li.infolabels.get('mediatype') == 'episode':
            return self.trakt_syncdata.get_episode_playcount(
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                season=li.infolabels.get('season'),
                episode=li.infolabels.get('episode')) or 0

        if li.infolabels.get('mediatype') == 'tvshow':
            air_count = self.trakt_syncdata.get_episode_airedcount(
                tmdb_id=li.unique_ids.get('tvshow.tmdb') or li.unique_ids.get('tmdb'))
            if air_count and air_count > 0:
                li.infolabels['episode'] = air_count
            air_count = max(int(li.infolabels.get('episode') or 0), int(air_count or 0), 0)
            return min(self.trakt_syncdata.get_episode_watchedcount(
                tmdb_id=li.unique_ids.get('tvshow.tmdb') or li.unique_ids.get('tmdb')) or 0, air_count)

        if li.infolabels.get('mediatype') == 'season':
            air_count = self.trakt_syncdata.get_episode_airedcount(
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                season=li.infolabels.get('season'))
            if air_count and air_count > 0:
                li.infolabels['episode'] = air_count
            air_count = max(int(li.infolabels.get('episode') or 0), int(air_count or 0), 0)
            return min(self.trakt_syncdata.get_episode_watchedcount(
                tmdb_id=li.unique_ids.get('tvshow.tmdb'),
                season=li.infolabels.get('season')) or 0, air_count)
