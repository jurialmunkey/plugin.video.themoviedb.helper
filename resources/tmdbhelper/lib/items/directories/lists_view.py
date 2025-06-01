from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, ContainerCacheOnlyDirectory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.addon.plugin import convert_type


class ListFanart(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('fanart', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListPoster(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('poster', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListImage(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('image', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListThumb(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('thumb', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListCast(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('castmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListCrew(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('crewmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListSeries(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('seriesmovies', 'collection', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredMovies(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('starredmovies', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredTvshows(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('starredtvshows', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListStarredCombined(ContainerDefaultCacheDirectory):

    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('starredcombined', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties']['tmdb_type'] == 'movie'])
            shows_count = len(sync.data) - movie_count
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('tv', 'container') if shows_count > movie_count else convert_type('movie', 'container')
        return sync.data


class ListCrewedMovies(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListCrewedTvshows(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('crewedtvshows', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListCrewedCombined(ContainerDefaultCacheDirectory):

    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('crewedcombined', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties']['tmdb_type'] == 'movie'])
            shows_count = len(sync.data) - movie_count
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('tv', 'container') if shows_count > movie_count else convert_type('movie', 'container')
        return sync.data


class ListCreditsCombined(ContainerDefaultCacheDirectory):
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('creditscombined', 'person', tmdb_id, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties']['tmdb_type'] == 'movie'])
            shows_count = len(sync.data) - movie_count
        except TypeError:
            return

        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('tv', 'container') if shows_count > movie_count else convert_type('movie', 'container')
        return sync.data


class ListVideos(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, **kwargs):
        sync = BaseViewFactory('videos', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('video', 'container')
        return sync.data
