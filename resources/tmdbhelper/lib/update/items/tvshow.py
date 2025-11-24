from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia


class LibraryTvshow(LibraryMedia):

    tmdb_type = 'tv'
    mediatype = 'tvshow'
    base_type = 'tvshows'
    forced = False

    strm_filename = None
    strm_contents = None

    @cached_property
    def cache(self):
        from tmdbhelper.lib.update.cacher import LibraryUpdateTvshowCacher
        cache = LibraryUpdateTvshowCacher(self.tmdb_id)
        cache.forced = self.forced
        return cache

    @property
    def log_check(self):
        log_check = self.cache.next_check
        if not log_check:
            self.cache.make_new_cache(self.name)
            self.cache.set_next_check(
                next_aired=self.next_aired,
                last_aired=self.last_aired,
                status=self.status)
            return
        return log_check

    """
    Sync Data
    """

    @cached_property
    def seasons_sync(self):
        from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
        try:
            return BaseViewFactory('seasons', 'tv', int(self.tmdb_id))
        except TypeError:
            return

    @cached_property
    def seasons_sync_data(self):
        if not self.seasons_sync:
            return
        return self.seasons_sync.data

    @cached_property
    def seasons(self):
        if not self.seasons_sync_data:
            return []
        return [
            i for i in (
                self.get_season(season)
                for season in self.seasons_sync_data
            ) if i.season != 0
        ]

    def get_season(self, sync_data):
        from tmdbhelper.lib.update.items.season import LibrarySeason
        season = LibrarySeason(self.tmdb_id)
        season.sync_data = self.key_getter(sync_data)
        season.cache = self.cache
        season.tvshow_id = self.tvshow_id
        season.folders = self.folders + season.folders
        return season

    """
    Meta Data
    """

    @cached_property
    def next_aired(self):
        return self.sync_data.get_key('next_episode_to_air') or {}

    @cached_property
    def last_aired(self):
        return self.sync_data.get_key('last_episode_to_air') or {}

    @cached_property
    def status(self):
        return self.sync_data.get_key('status')

    """
    Kodi Data
    """

    @cached_property
    def tvshow_id(self):
        return self.get_kodi_info(
            info='dbid',
            imdb_id=self.imdb_id,
            tmdb_id=self.tmdb_id,
            tvdb_id=self.tvdb_id
        )
