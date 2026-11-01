from tmdbhelper.lib.sync.providers.ratings import RatingsSupplier


class OMDbRatingsSupplier(RatingsSupplier):
    def get_ratings(self):
        if not self.provider.is_authorized() or not self.imdb_id:
            return {}
        try:
            return self.provider.api.get_ratings_awards(imdb_id=self.imdb_id) or {}
        except (KeyError, TypeError, IndexError, ValueError):
            return {}
