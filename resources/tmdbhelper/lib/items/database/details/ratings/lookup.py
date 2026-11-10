from threading import Lock
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings import (
    RatingsDict,
    RatingsEpisodesDict,
    RatingsItemIds,
    RatingsSeasonsDict,
)
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings_entries import RatingsStoredData
from tmdbhelper.lib.items.database.details.ratings.progress import DetailsRatingsProgress


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
    Every level's providers are asked online in parallel. Online ratings are returned before
    they are saved. With allow_stale, expired ratings are returned for the caller to refresh
    separately. The ratings so far are published to progress as each provider finishes."""

    def __init__(self, item, common_apis, ratings_settings, allow_stale=False):
        self.item = item
        self.common_apis = common_apis
        self.ratings_settings = ratings_settings
        self.allow_stale = allow_stale
        self.publish_lock = Lock()  # One update at a time, so that an earlier one never replaces a later one

    @cached_property
    def progress(self):
        return self.get_progress()

    def get_progress(self):
        """Replaced by the worker's progress for lookups that monitors wait on."""
        return DetailsRatingsProgress()

    @cached_property
    def item_ids(self):
        return self.get_item_ids()

    def get_item_ids(self):
        """Shared by every level: each level's suppliers look items up by the show's IMDb ID."""
        return RatingsItemIds(self.item.tmdb_type, self.item.request.tmdb_id, self.common_apis.tmdb_api)

    @cached_property
    def item_levels(self):
        return self.get_item_levels()

    def get_item_levels(self):
        request = self.item.request
        levels = (
            self.get_level(RatingsDict),
            self.get_level(RatingsSeasonsDict, request.season),
            self.get_level(RatingsEpisodesDict, request.season, request.episode),
        )
        return tuple(level for level in levels if level.data_cond)

    @cached_property
    def stored_data(self):
        return self.get_stored_data()

    def get_stored_data(self):
        """Saved ratings for every level, read with one query per table."""
        return RatingsStoredData((level.item_id for level in self.item_levels), common_apis=self.common_apis)

    @cached_property
    def levels(self):
        return self.get_levels()

    def get_levels(self):
        """The item's levels, sharing one read of their saved ratings."""
        for level in self.item_levels:
            level.stored_data = self.stored_data
        return self.item_levels

    def get_level(self, level_class, season=None, episode=None):
        level = level_class(common_apis=self.common_apis)
        level.tmdb_type = self.item.tmdb_type
        level.tmdb_id = self.item.request.tmdb_id
        level.season = season
        level.episode = episode
        level.ratings_settings = self.ratings_settings
        level.item_ids = self.item_ids
        level.allow_stale = self.allow_stale
        return level

    @cached_property
    def entries(self):
        return self.get_entries()

    def get_entries(self):
        """Every level's providers, with their saved values read and their Top 250 rank."""
        self.ratings_settings.providers
        for attr in ('stored_values', 'expiries'):
            getattr(self.stored_data, attr)
        for level in self.levels:
            level.top250
        return tuple(entry for level in self.levels for entry in level.entries)

    @property
    def resolved_entries(self):
        return tuple(entry for entry in self.entries if entry.is_resolved)

    @property
    def received(self):
        """Providers whose values are known and not empty."""
        return sum(1 for entry in self.resolved_entries if entry.values)

    @staticmethod
    def get_merged_ratings(levels_ratings):
        """Later levels replace the show's values, as episodes and seasons did before."""
        return {
            key: value
            for ratings in levels_ratings
            for key, value in ratings.items()
        }

    @property
    def partial_ratings(self):
        return self.get_merged_ratings(level.partial_ratings for level in self.levels)

    def publish(self, is_online):
        """Counted before the values are merged, so that the values include every provider counted."""
        with self.publish_lock:
            received = self.received
            self.progress.update(self.partial_ratings, received, is_online)

    def fetch_entry(self, entry):
        entry.fetch()
        if entry.values:
            self.publish(is_online=True)

    def fetch_online(self):
        """Ask every level's providers that need it, in parallel."""
        entries = tuple(entry for entry in self.entries if entry.is_online_needed)
        if not entries:
            return
        with ParallelThread(entries, self.fetch_entry):
            pass

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        self.publish(is_online=False)
        self.fetch_online()
        return self.get_merged_ratings(level.ratings for level in self.levels)

    @cached_property
    def expiry(self):
        return self.get_expiry()

    def get_expiry(self):
        return min(level.ratings_expiry for level in self.levels)

    @property
    def is_stale(self):
        return any(level.is_stale for level in self.levels)

    @property
    def unsaved_levels(self):
        return tuple(level for level in self.levels if level.is_unsaved)

    def save(self):
        for level in self.unsaved_levels:
            level.save_online_ratings()
