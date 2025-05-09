from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, ContainerCacheOnlyDirectory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.addon.plugin import convert_type


class ListFanart(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('fanart', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListPoster(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('poster', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListImage(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('image', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListThumb(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('thumb', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListCast(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('castmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListCrew(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('crewmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListStarredMovies(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('starredmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredTvshows(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('starredtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListStarredCombined(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('starredmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        movies_data = sync.data or []
        sync = BaseViewFactory('starredtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        tvshows_data = sync.data or []
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('movie' if len(movies_data) >= len(tvshows_data) else 'tv', 'container')
        return sorted(movies_data + tvshows_data, key=lambda x: x['infolabels']['votes'] or 0, reverse=True)


class ListCrewedMovies(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListCrewedTvshows(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('crewedtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListCrewedCombined(ContainerDefaultCacheDirectory):
    # @timer_method
    def get_items(self, tmdb_id, limit=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        movies_data = sync.data or []
        sync = BaseViewFactory('crewedtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        tvshows_data = sync.data or []
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('movie' if len(movies_data) >= len(tvshows_data) else 'tv', 'container')
        return sorted(movies_data + tvshows_data, key=lambda x: x['infolabels']['votes'] or 0, reverse=True)


class ListCreditsCombined(ContainerDefaultCacheDirectory):
    def get_items(self, tmdb_id, limit=None, **kwargs):
        movies_data = []
        tvshows_data = []
        sync = BaseViewFactory('starredmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        movies_data += sync.data or []
        sync = BaseViewFactory('starredtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        tvshows_data += sync.data or []
        sync = BaseViewFactory('crewedmovies', 'person', tmdb_id, filters=self.filters, limit=limit)
        movies_data += sync.data or []
        sync = BaseViewFactory('crewedtvshows', 'person', tmdb_id, filters=self.filters, limit=limit)
        tvshows_data += sync.data or []

        titles = []

        def label_check(i):
            if i['infolabels']['title'] in titles:
                return
            titles.append(i['infolabels']['title'])
            return i

        unique_tvshows_data = [j for j in (label_check(i) for i in tvshows_data) if j]
        unique_movies_data = [j for j in (label_check(i) for i in movies_data) if j]

        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('movie' if len(unique_movies_data) >= len(unique_tvshows_data) else 'tv', 'container')
        return sorted(unique_movies_data + unique_tvshows_data, key=lambda x: x['infolabels']['votes'] or 0, reverse=True)


class ListVideos(ContainerCacheOnlyDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('videos', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('video', 'container')
        return sync.data
