from jurialmunkey.ftools import cached_property


class CommonContainerAPIs():
    @cached_property
    def all_awards(self):
        return self.get_awards_data()

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def tmdb_imagepath(self):
        from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
        return TMDbImagePath()

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def ftv_api(self):
        from tmdbhelper.lib.api.fanarttv.api import FanartTV
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('fanarttv_lookup'):
            return
        return FanartTV()

    @cached_property
    def tvdb_api(self):
        from tmdbhelper.lib.api.tvdb.api import TVDb
        return TVDb()

    @cached_property
    def mdblist_api(self):
        from tmdbhelper.lib.api.mdblist.api import MDbList
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('mdblist_apikey', 'str'):
            return
        return MDbList()

    @cached_property
    def omdb_api(self):
        from tmdbhelper.lib.api.omdb.api import OMDb
        from tmdbhelper.lib.addon.plugin import get_setting
        if not get_setting('omdb_apikey', 'str'):
            return
        return OMDb()

    @cached_property
    def query_database(self):
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        return FindQueriesDatabase()
