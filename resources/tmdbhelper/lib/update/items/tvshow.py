from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia
from tmdbhelper.lib.addon.plugin import get_setting


class LibraryTvshow(LibraryMedia):

    sync_type = 'tvshow'
    basedir = get_setting('tvshows_library', 'str') or 'special://profile/addon_data/plugin.video.themoviedb.helper/tvshows/'

    @cached_property
    def tvshowtitle(self):
        return self.infolabels.get_key('tvshowtitle')

    @cached_property
    def cache(self):
        from tmdbhelper.lib.update.cacher import LibraryUpdateTvshowCacher
        return LibraryUpdateTvshowCacher(self.tmdb_id, self.force)

    def set_next(self):
        self.cache.create_new_cache(self.name)
        self.cache.set_next_check(  # TODO: FIX ME
            next_aired=self.next_aired,
            last_aired=self.last_aired,
            status=self.status
        )

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
            ) if i.number != 0
        ]

    def get_season(self, sync_data):
        from tmdbhelper.lib.update.items.season import LibrarySeason
        season = LibrarySeason(self.tmdb_id)
        season.sync_data = self.key_getter(sync_data)
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
    def dbid(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('tv').get_info(
            info='dbid',
            imdb_id=self.imdb_id,
            tmdb_id=self.tmdb_id,
            tvdb_id=self.tvdb_id
        )

    def get_episode_db_info(self, season, episode, info='dbid'):
        if not self.dbid:
            return
        from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
        return KodiLibrary(
            dbtype='episode',
            tvshowid=self.dbid,
            logging=False
        ).get_info(
            info=info,
            season=season,
            episode=episode
        )
