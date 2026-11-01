from tmdbhelper.lib.sync.providers.ratings import RatingsSupplier


class TMDbRatingsSupplier(RatingsSupplier):
    def get_ratings(self):
        data = self.provider.api.get_response_json(self.tmdb_type, self.tmdb_id)
        if not data:
            return {}
        try:
            return {
                'tmdb_rating': int(data['vote_average'] * 10),
                'tmdb_votes': data['vote_count']
            }
        except (KeyError, TypeError, IndexError, ValueError):
            return {}
