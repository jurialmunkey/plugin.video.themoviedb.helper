from threading import Lock
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.consts import DAY_IN_SECONDS
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.ratings_entries import (
    RatingsProviderEntry,
    RatingsStoredData,
    RatingsTop250Rank,
)
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings


class RatingsItemIds:
    """ Identifiers that ratings suppliers look items up by. The IMDb ID is looked up once,
    on first use, so that suppliers which only need the TMDb ID never wait for it """

    def __init__(self, tmdb_type, tmdb_id, tmdb_api):
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.tmdb_api = tmdb_api
        self.lock = Lock()  # Per item, so that lookups for other items do not wait

    @property
    def imdb_id(self):
        with self.lock:
            return self.cached_imdb_id

    @cached_property
    def cached_imdb_id(self):
        return self.get_imdb_id()

    def get_imdb_id(self):
        database = FindQueriesDatabase()
        database.tmdb_api = self.tmdb_api
        return database.get_external_ids(self.tmdb_type, self.tmdb_id).get('imdb')


class RatingsDict(BaseList):
    """ An item's ratings at one level (show, season or episode), merged from its providers.

    Each provider's values are saved as one row per key, with the provider's expiry saved
    separately. Only providers that are missing or expired are asked online. For each key,
    current values beat expired ones, and within each the preferred provider's value wins.
    """

    expiry_time = 7 * 86400
    stale_grace = 30 * DAY_IN_SECONDS  # Expired ratings are shown while they refresh until this passes
    table = 'ratings'
    provider_table = 'ratings_provider'
    placeholder_keys = ('id', 'mediatype', 'expiry', 'language')
    allow_stale = False  # Return expired ratings for the caller to refresh separately

    ratings_style = {
        'tmdb_rating': lambda v: f'{(v / 10):.1f}',
        'trakt_rating': lambda v: f'{(v / 10):.1f}',
        'imdb_rating': lambda v: f'{(v / 10):.1f}',
        'metacriticuser_rating': lambda v: f'{(v / 10):.1f}',
        'letterboxd_rating': lambda v: f'{(v / 20):.1f}',  # 5 Star rating
        'rogerebert_rating': lambda v: f'{(v / 25):.1f}',  # 4 Star rating
        'myanimelist_rating': lambda v: f'{(v / 10):.1f}',
    }

    @property
    def deletion(self):
        """ Lease that keeps the item until its expired ratings can no longer be shown """
        return self.expiry + self.stale_grace

    @cached_property
    def ratings_settings(self):
        return self.get_ratings_settings()

    def get_ratings_settings(self):
        return RatingsProviderSettings()

    @cached_property
    def mediatype(self):
        return self.get_mediatype()

    def get_mediatype(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type == 'tv':
            return 'tvshow'

    @cached_property
    def item_ids(self):
        return self.get_item_ids()

    def get_item_ids(self):
        return RatingsItemIds(self.tmdb_type, self.tmdb_id, self.common_apis.tmdb_api)

    @cached_property
    def stored_data(self):
        return self.get_stored_data()

    def get_stored_data(self):
        return RatingsStoredData((self.item_id, ), common_apis=self.common_apis)

    @cached_property
    def provider_keys(self):
        return tuple(self.cache.ratings_provider_columns.keys())

    @cached_property
    def suppliers(self):
        return self.get_suppliers()

    def get_suppliers(self):
        """ (provider ID, supplier) for each enabled provider, in the preferred order """
        providers = self.ratings_settings.get_enabled_providers(self.mediatype)
        return tuple(
            (provider.provider_id, self.get_provider_supplier(provider))
            for provider in providers
        )

    def get_provider_supplier(self, provider):
        return provider.ratings_classes[self.mediatype](
            provider=provider, tmdb_type=self.tmdb_type, tmdb_id=self.tmdb_id,
            item_ids=self.item_ids, season=self.season, episode=self.episode)

    @cached_property
    def entries(self):
        return self.get_entries()

    def get_entries(self):
        return tuple(
            RatingsProviderEntry(self, provider_id, supplier)
            for provider_id, supplier in self.suppliers
        )

    @property
    def resolved_entries(self):
        return tuple(entry for entry in self.entries if entry.is_resolved)

    @cached_property
    def merged_values(self):
        return self.get_merged_values(self.entries)

    @staticmethod
    def get_merged_values(entries):
        """ Expired values first and current values last, each from the least preferred
        provider to the most preferred, so that later values replace earlier ones """
        stale_entries = tuple(entry for entry in entries if entry.is_stale)
        current_entries = tuple(entry for entry in entries if entry.is_current)
        return {
            key: value
            for entries in (stale_entries, current_entries)
            for entry in reversed(entries)
            for key, value in entry.values.items()
        }

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        """ Providers that need it are asked online one at a time, unless fetched beforehand """
        if not self.data_cond:
            return {}
        return self.map_values({**self.merged_values, **self.top250})

    @property
    def partial_ratings(self):
        return self.get_partial_ratings()

    def get_partial_ratings(self):
        """ The ratings of the providers that have finished, while others are still asked online """
        if not self.data_cond:
            return {}
        return self.map_values({**self.get_merged_values(self.resolved_entries), **self.top250})

    @cached_property
    def top250(self):
        return self.get_top250()

    def get_top250(self):
        return RatingsTop250Rank(self.tmdb_type, self.tmdb_id).values

    def get_data(self):
        """ The ratings; any retrieved online are saved by save_online_ratings() """
        return self.ratings

    @property
    def is_stale(self):
        return any(entry.is_stale for entry in self.entries)

    @property
    def unsaved_entries(self):
        return tuple(entry for entry in self.entries if entry.is_unsaved)

    @property
    def is_unsaved(self):
        return bool(self.unsaved_entries)

    @property
    def ratings_expiry(self):
        return min(
            (entry.expiry for entry in self.entries if entry.expiry is not None),
            default=self.expiry,
        )

    def map_values(self, values):
        mapped_data = {}

        for k, v in values.items():

            if v in (None, ''):
                continue

            if v == 0 and k.endswith(('_wins', '_nominations')):
                continue

            mapped_data[k] = v

            if not isinstance(v, int):
                continue

            if not k.endswith('_rating'):
                mapped_data[f'comma_{k}'] = f'{v:,d}'
                continue

            mapped_data[f'percent_{k}'] = v
            mapped_data[f'decimal_{k}'] = f'{(v / 10):.1f}'
            mapped_data[f'starred_{k}'] = f'{(v / 20):.1f}'

            try:
                mapped_data[k] = self.ratings_style[k](v)
            except KeyError:
                mapped_data[k] = v

        return mapped_data

    @property
    def placeholder_values(self):
        """ A placeholder item row for the ratings to link to, as cast members have """
        return (self.item_id, self.mediatype, 0, self.common_apis.tmdb_api.language)

    def save_online_ratings(self):
        """ Replace the saved values of each provider retrieved online, in one transaction.
        Saving does not wait for item details: the placeholder row never replaces them """
        with self.connection.open():
            self.connection.open_connection.execute('BEGIN')
            self.set_or_update_null_cached_list_values('baseitem', self.placeholder_keys, self.placeholder_values)
            for entry in self.unsaved_entries:
                self.save_entry(entry)
            self.set_cached_deletion((self.item_id, ), self.deletion)  # Keep the item while its ratings can be shown
            self.connection.open_connection.execute('COMMIT')

    def save_entry(self, entry):
        """ Keys that the provider no longer returns are removed with its previous values """
        self.cache.del_list_values(
            self.table, values=entry.key, conditions='id=? AND provider=?', connection=self.open_connection)
        self.set_cached_list_values(self.table, self.keys, entry.saved_rows, overwrite=True)
        self.set_cached_list_values(self.provider_table, self.provider_keys, entry.saved_expiry_row, overwrite=True)


class RatingsSeasonsDict(RatingsDict):
    def get_top250(self):
        """ Only movies and shows have a Top 250 rank """
        return {}

    def get_mediatype(self):
        return 'season'

    @property
    def data_cond(self):
        """ Season ratings only apply to a TV item with a season """
        if self.tmdb_type != 'tv':
            return False
        if self.season is None:
            return False
        return super().data_cond

    @property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)


class RatingsEpisodesDict(RatingsSeasonsDict):
    def get_mediatype(self):
        return 'episode'

    @property
    def data_cond(self):
        """ Episode ratings only apply to a TV item with a season and an episode """
        if self.episode is None:
            return False
        return super().data_cond

    @property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)
