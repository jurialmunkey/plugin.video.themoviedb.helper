from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia


class LibraryEpisode(LibraryMedia):

    strm_fstr = 'plugin://plugin.video.themoviedb.helper/?info=play&tmdb_type=tv&islocal=True&tmdb_id={tmdb_id}&season={season}&episode={episode}'
    mediatype = 'episode'
    base_type = 'tvshows'
    tmdb_type = 'tv'
    tvshow_id = None

    @cached_property
    def folders(self):
        return []

    @cached_property
    def episode(self):
        return self.infolabels.get_key('episode') or 0

    @cached_property
    def season(self):
        return self.infolabels.get_key('season') or 0

    def get_name(self):
        from jurialmunkey.parser import try_int
        from tmdbhelper.lib.files.futils import validify_filename
        return validify_filename(f'S{try_int(self.season):02d}E{try_int(self.episode):02d} - {self.title}')

    @cached_property
    def strm_contents(self):
        if not self.tmdb_id:
            return
        if not self.season:
            return
        if not self.episode:
            return
        return self.strm_fstr.format(tmdb_id=self.tmdb_id, season=self.season, episode=self.episode)

    info_filename = None
    info_contents = None

    @cached_property
    def library_file(self):
        return self.get_kodi_info(info='file')

    @cached_property
    def kodidb(self):
        if not self.tvshow_id:
            return
        from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
        return KodiLibrary(
            dbtype='episode',
            tvshowid=self.tvshow_id,
            logging=False
        )

    def get_kodi_info(self, info='dbid'):
        if not self.kodidb:
            return
        return self.kodidb.get_info(
            info=info,
            season=self.season,
            episode=self.episode
        )
