from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory, ContainerCacheOnlyDirectory
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import convert_type, get_setting
from jurialmunkey.parser import try_int


class ListConfigureOffset:
    def __init__(self, func):
        self.func = func

    @cached_property
    def offset(self):
        if not self.limit:
            return
        if not self.page:
            return
        return ((self.limit * self.page) - self.limit)

    @cached_property
    def items(self):
        limit = None if not self.limit else (self.limit + 1)
        return self.func(self.inst, *self.args, limit=limit, offset=self.offset, **self.kwgs)

    @cached_property
    def finalised_items(self):
        if not self.items:
            return
        if not self.limit or len(self.items) <= self.limit:
            return self.items
        self.items[-1] = {'next_page': self.page + 1}
        return self.items

    @cached_property
    def limit(self):
        return (
            self.pmax if self.inst.is_cacheonly else
            min((20 * get_setting('pagemulti_sync', 'int')), self.pmax)
        )

    def __get__(self, obj, obj_type):
        """Support instance methods."""
        import functools
        return functools.partial(self.__call__, obj)

    def __call__(self, inst, *args, limit=None, page=None, **kwgs):
        self.inst = inst
        self.args = args
        self.kwgs = kwgs
        self.page = try_int(page, fallback=1)
        self.pmax = try_int(limit, fallback=None) or 250
        return self.finalised_items


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

    @ListConfigureOffset
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('castmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListCrew(ContainerCacheOnlyDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, tmdb_type, season=None, episode=None, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('crewmember', tmdb_type, tmdb_id, season, episode, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.container_content = convert_type('person', 'container')
        return sync.data


class ListSeries(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('seriesmovies', 'collection', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredMovies(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('starredmovies', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListStarredTvshows(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('starredtvshows', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListStarredCombined(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('starredcombined', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties'].get('tmdb_type') == 'movie'])
            shows_count = len(sync.data) - movie_count
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('tv', 'container') if shows_count > movie_count else convert_type('movie', 'container')
        return sync.data


class ListCrewedMovies(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('crewedmovies', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('movie')
        self.container_content = convert_type('movie', 'container')
        return sync.data


class ListCrewedTvshows(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('crewedtvshows', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        self.kodi_db = self.get_kodi_database('tv')
        self.container_content = convert_type('tv', 'container')
        return sync.data


class ListCrewedCombined(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('crewedcombined', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)
        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties'].get('tmdb_type') == 'movie'])
            shows_count = len(sync.data) - movie_count
        except TypeError:
            return
        self.kodi_db = self.get_kodi_database('both')
        self.container_content = convert_type('tv', 'container') if shows_count > movie_count else convert_type('movie', 'container')
        return sync.data


class ListCreditsCombined(ContainerDefaultCacheDirectory):

    @ListConfigureOffset
    def get_items(self, tmdb_id, limit=None, sort_by=None, sort_how=None, offset=None, **kwargs):
        sync = BaseViewFactory('creditscombined', 'person', tmdb_id, filters=self.filters, limit=limit, offset=offset, sort_by=sort_by, sort_how=sort_how)

        try:
            movie_count = len([i for i in sync.data if i and i['infoproperties'].get('tmdb_type') == 'movie'])
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
