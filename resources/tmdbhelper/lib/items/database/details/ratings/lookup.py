from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings import (
    RatingsDict,
    RatingsEpisodesDict,
    RatingsSeasonsDict,
)


class DetailsRatingsItem:
    """The rated item that a details request refers to.
    Movies and TV shows have ratings, including a show's seasons and episodes."""

    tmdb_types = {
        'movie': 'movie',
        'tvshow': 'tv',
        'season': 'tv',
        'episode': 'tv',
    }

    def __init__(self, request):
        self.request = request

    @property
    def is_rated(self):
        return self.request.mediatype in self.tmdb_types

    @cached_property
    def tmdb_type(self):
        return self.tmdb_types[self.request.mediatype]

    @cached_property
    def key(self):
        return (self.tmdb_type, self.request.tmdb_id, self.request.season, self.request.episode)


class DetailsRatingsLookup:
    """Ratings for an item's show, season and episode levels, from the ratings table or online.
    Online ratings are returned before they are saved."""

    def __init__(self, item, common_apis, ratings_settings):
        self.item = item
        self.common_apis = common_apis
        self.ratings_settings = ratings_settings

    @cached_property
    def levels(self):
        return self.get_levels()

    def get_levels(self):
        request = self.item.request
        levels = (
            self.get_level(RatingsDict),
            self.get_level(RatingsSeasonsDict, request.season),
            self.get_level(RatingsEpisodesDict, request.season, request.episode),
        )
        return tuple(level for level in levels if level.data_cond)

    def get_level(self, level_class, season=None, episode=None):
        level = level_class(common_apis=self.common_apis)
        level.tmdb_type = self.item.tmdb_type
        level.tmdb_id = self.item.request.tmdb_id
        level.season = season
        level.episode = episode
        level.ratings_settings = self.ratings_settings
        return level

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        """Later levels replace the show's values, as episodes and seasons did before."""
        return {
            key: value
            for level in self.levels
            for key, value in level.ratings.items()
        }

    @cached_property
    def expiry(self):
        return self.get_expiry()

    def get_expiry(self):
        return min(level.ratings_expiry for level in self.levels)

    @property
    def unsaved_levels(self):
        return tuple(level for level in self.levels if level.is_unsaved)

    def save(self):
        for level in self.unsaved_levels:
            level.save_online_ratings()
