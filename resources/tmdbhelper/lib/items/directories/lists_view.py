from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.addon.plugin import convert_type


class ListFanart(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('fanart', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListPoster(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('poster', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListImage(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('image', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListThumb(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('thumb', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('image', 'container')
        return sync.data


class ListCast(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('castmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListCrew(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('crewmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListStarredMovies(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('starredmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredTvshows(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('starredtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListStarredCombined(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('starredmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        movies_data = sync.data or []
        sync = BaseViewFactory('starredtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        tvshows_data = sync.data or []
        self.container_content = convert_type('movie' if len(movies_data) >= len(tvshows_data) else 'tv', 'container')
        return sorted(movies_data + tvshows_data, key=lambda x: x['infolabels']['votes'], reverse=True)


class ListCrewedMovies(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListCrewedTvshows(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('crewedtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListCrewedCombined(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        movies_data = sync.data or []
        sync = BaseViewFactory('crewedtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        tvshows_data = sync.data or []
        self.container_content = convert_type('movie' if len(movies_data) >= len(tvshows_data) else 'tv', 'container')
        return sorted(movies_data + tvshows_data, key=lambda x: x['infolabels']['votes'], reverse=True)


class ListCreditsCombined(ContainerDirectory):
    # @timer_method
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        movies_data = []
        tvshows_data = []
        sync = BaseViewFactory('starredmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        movies_data += sync.data or []
        sync = BaseViewFactory('starredtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        tvshows_data += sync.data or []
        sync = BaseViewFactory('crewedmovies', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        movies_data += sync.data or []
        sync = BaseViewFactory('crewedtvshows', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        tvshows_data += sync.data or []

        titles = []

        def label_check(i):
            if i['infolabels']['title'] in titles:
                return
            titles.append(i['infolabels']['title'])
            return i

        unique_tvshows_data = [j for j in (label_check(i) for i in tvshows_data) if j]
        unique_movies_data = [j for j in (label_check(i) for i in movies_data) if j]

        self.container_content = convert_type('movie' if len(unique_movies_data) >= len(unique_tvshows_data) else 'tv', 'container')
        return sorted(unique_movies_data + unique_tvshows_data, key=lambda x: x['infolabels']['votes'], reverse=True)


class ListVideos(ContainerDirectory):
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, **kwargs):
        sync = BaseViewFactory('videos', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit)
        self.container_content = convert_type('video', 'container')
        return sync.data
