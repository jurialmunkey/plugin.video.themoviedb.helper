from tmdbhelper.lib.update.items.media import LibraryMedia
from tmdbhelper.lib.addon.plugin import get_setting


class LibraryMovie(LibraryMedia):

    sync_type = 'movie'
    strm_fstr = 'plugin://plugin.video.themoviedb.helper/?info=play&tmdb_id={}&tmdb_type=movie&islocal=True'
    basedir = get_setting('movies_library', 'str') or 'special://profile/addon_data/plugin.video.themoviedb.helper/movies/'
