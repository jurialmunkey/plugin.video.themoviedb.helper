from jurialmunkey.ftools import cached_property


IMDB_TOP250_MEDIATYPES = ('movie', 'tvshow')


class IMDbTop250Supplier:
    def __init__(self, provider, tmdb_type):
        self.provider = provider
        self.tmdb_type = tmdb_type

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        raise NotImplementedError


class IMDbTop250:
    def __init__(self, tmdb_type, settings=None):
        self.tmdb_type = tmdb_type
        self._settings = settings

    @cached_property
    def settings(self):
        return self.get_settings()

    def get_settings(self):
        from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings
        return self._settings if self._settings is not None else RatingsProviderSettings()

    @cached_property
    def mediatype(self):
        return {'movie': 'movie', 'tv': 'tvshow'}[self.tmdb_type]

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        return tuple(
            provider for provider in self.settings.get_enabled_providers(self.mediatype)
            if self.mediatype in provider.imdb_top250_classes)

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        for provider in self.providers:
            supplier = provider.imdb_top250_classes[self.mediatype](provider, self.tmdb_type)
            if supplier.items:
                return supplier.items
        return []
