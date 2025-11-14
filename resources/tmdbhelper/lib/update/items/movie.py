from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia


class LibraryMovie(LibraryMedia):

    mediatype = 'movie'
    tmdb_type = 'movie'
    strm_fstr = 'plugin://plugin.video.themoviedb.helper/?info=play&tmdb_id={tmdb_id}&tmdb_type=movie&islocal=True'
    base_type = 'movies'

    @cached_property
    def library_file(self):
        return self.get_kodi_info(
            info='file',
            imdb_id=self.imdb_id,
            tmdb_id=self.tmdb_id
        )
