from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.basemeta_factories.factory import BaseMetaFactory
from tmdbhelper.lib.sync.providers.ratings import RatingsSupplier


class TMDbRatingsSupplier(RatingsSupplier):
    stored_data_routes = {
        'movie': 'movie_tmdb_rating',
        'tv': 'tvshow_tmdb_rating',
    }

    @cached_property
    def stored_data(self):
        return self.get_stored_data()

    def get_stored_data(self):
        """The rating stored with the item's details, so cached items need no TMDb request."""
        reader = BaseMetaFactory(self.stored_data_routes[self.tmdb_type])
        reader.item_id = reader.get_base_id(self.tmdb_type, self.tmdb_id)
        return reader.data

    @cached_property
    def online_data(self):
        return self.get_online_data()

    def get_online_data(self):
        return self.provider.api.get_response_json(self.tmdb_type, self.tmdb_id)

    def get_ratings(self):
        data = self.stored_data or self.online_data
        if not data:
            return {}
        try:
            return {
                'tmdb_rating': int(data['vote_average'] * 10),
                'tmdb_votes': data['vote_count']
            }
        except (KeyError, TypeError, IndexError, ValueError):
            return {}
