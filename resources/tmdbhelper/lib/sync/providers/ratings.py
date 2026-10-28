from jurialmunkey.ftools import cached_property


RATINGS_MEDIATYPES = ('movie', 'tvshow', 'season', 'episode')


class RatingsSupplier:
    def __init__(
            self, provider, tmdb_type, tmdb_id,
            imdb_id=None, season=None, episode=None):
        self.provider = provider
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.season = season
        self.episode = episode

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        raise NotImplementedError
