from jurialmunkey.ftools import cached_property


class CommonContainerAPIs():
    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @cached_property
    def ftv_api(self):
        from tmdbhelper.lib.api.fanarttv.api import FanartTV
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('fanarttv_lookup'):
            return
        return FanartTV()

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()
