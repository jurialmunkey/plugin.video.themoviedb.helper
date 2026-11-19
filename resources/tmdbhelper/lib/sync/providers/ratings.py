from jurialmunkey.ftools import cached_property


RATINGS_MEDIATYPES = ('movie', 'tvshow', 'season', 'episode')


class RatingsSupplier:
    def __init__(
            self, provider, tmdb_type, tmdb_id,
            item_ids, season=None, episode=None):
        self.provider = provider
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.item_ids = item_ids
        self.season = season
        self.episode = episode

    @property
    def imdb_id(self):
        """Looked up on first use, so that suppliers which do not need it never wait for it."""
        return self.item_ids.imdb_id

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        raise NotImplementedError
