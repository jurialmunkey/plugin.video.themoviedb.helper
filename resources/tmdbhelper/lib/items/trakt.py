from tmdbhelper.lib.files.ftools import cached_property


class TraktPlayData():
    def __init__(self, pauseplayprogress=False, watchedindicators=False, unwatchedepisodes=False, traktepisodetypes=True):
        self._pauseplayprogress = pauseplayprogress  # Set play progress using paused at position
        self._watchedindicators = watchedindicators  # Set watched status and playcount
        self._unwatchedepisodes = unwatchedepisodes  # Set unwatched episode count to total episode count for unwatched tvshows (if false)
        self._traktepisodetypes = traktepisodetypes  # Set episode_type property for episodes

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

    @cached_property
    def trakt_episodedata(self):
        return self.trakt_api.trakt_episodedata

    @is_sync
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

    @is_sync
    def set_episode_type(self, li):
        if not self._traktepisodetypes:
            return
        if li.infolabels.get('mediatype') != 'episode':
            return
        tmdb = li.tmdb_id
        snum = li.season
        enum = li.episode
        if not tmdb or not snum or not enum:
            return
        episode_type = self.trakt_episodedata.get_value(tmdb, snum, enum, key='episode_type')
        if not episode_type:
            return
        li.infoproperties['episode_type'] = episode_type

    @is_sync
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

    @is_sync
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
