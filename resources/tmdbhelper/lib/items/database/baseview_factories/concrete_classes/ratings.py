from threading import Lock
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.consts import DAY_IN_SECONDS
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings
from jurialmunkey.parser import try_int


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
    expiry_time = 7 * 86400
    deletion_grace = 30 * DAY_IN_SECONDS  # Expired ratings are kept to show while they refresh
    cached_data_table = table = 'ratings'
    cached_data_conditions = 'id=? AND provider_fingerprint=?'
    placeholder_keys = ('id', 'mediatype', 'expiry', 'language')
    allow_stale = False  # Return expired ratings for the caller to refresh separately

    ratings_sources = {
        'cached': 'cached_ratings',
        'stale': 'stale_ratings',
        'online': 'online_ratings',
    }

    rating_attribs = (
        'provider_ratings',
        'imdb_top250',
    )

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
    def cached_data_values(self):
        """ WHERE condition ? ? = value, value. Expired rows are read too """
        return (self.item_id, self.ratings_settings.fingerprint)

    @property
    def deletion(self):
        """ Lease that keeps the row long enough after expiry to show while it refreshes """
        return self.expiry + self.deletion_grace

    @cached_property
    def ratings_settings(self):
        return self.get_ratings_settings()

    def get_ratings_settings(self):
        return RatingsProviderSettings()

    @cached_property
    def mediatype(self):
        return self.get_mediatype()

    @cached_property
    def item_ids(self):
        return self.get_item_ids()

    def get_item_ids(self):
        return RatingsItemIds(self.tmdb_type, self.tmdb_id, self.common_apis.tmdb_api)

    @cached_property
    def imdb_top250_list(self):
        return self.get_imdb_top250_list()

    def get_mediatype(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type == 'tv':
            return 'tvshow'

    def get_imdb_top250_list(self):
        return FindQueriesDatabase().get_imdb_top250_list_cached(self.tmdb_type)

    @cached_property
    def ratings_suppliers(self):
        return self.get_ratings_suppliers()

    def get_ratings_suppliers(self):
        providers = self.ratings_settings.get_enabled_providers(self.mediatype)
        return tuple(
            provider.ratings_classes[self.mediatype](
                provider=provider, tmdb_type=self.tmdb_type, tmdb_id=self.tmdb_id,
                item_ids=self.item_ids, season=self.season, episode=self.episode)
            for provider in providers)

    @cached_property
    def provider_ratings(self):
        return self.get_provider_ratings()

    @staticmethod
    def get_supplier_ratings(supplier):
        return supplier.ratings

    def get_provider_ratings(self):
        if not self.ratings_suppliers:
            return {}
        with ParallelThread(self.ratings_suppliers, self.get_supplier_ratings) as pt:
            items = pt.queue
        return {
            key: value for data in reversed(items) for key, value in data.items()
            if value not in (None, '')
        }

    @cached_property
    def imdb_top250(self):
        rank = self.get_imdb_top250_rank()
        return {'top250': rank} if rank else {}

    def get_imdb_top250_rank(self):
        if not self.imdb_top250_list:  # No provider supplies a Top 250 list
            return
        try:
            return self.imdb_top250_list.index(try_int(self.tmdb_id)) + 1  # Must be an int to match
        except ValueError:
            return

    @cached_property
    def online_data_mapped(self):
        return self.get_online_data_mapped()

    def get_online_data_mapped(self):
        """ function called when local cache does not have any data """

        def get_data_attr(attr):
            data = getattr(self, attr)
            return data or {}

        # precache some property values before threading; suppliers look up the IMDb ID if needed
        for attr in ('mediatype', 'ratings_suppliers'):
            getattr(self, attr)

        with ParallelThread(self.rating_attribs, get_data_attr) as pt:
            items = pt.queue

        return {k: v for d in items for k, v in d.items()}

    def configure_mapped_data(self, data):
        def get_value(k):
            if k == 'id':
                return self.item_id
            if k == 'expiry':
                return self.expiry
            if k == 'provider_fingerprint':
                return self.ratings_settings.fingerprint
            try:
                return data[k]
            except (TypeError, KeyError, IndexError, ValueError):
                return
        return [get_value(k) for k in self.keys]

    @cached_property
    def cached_row(self):
        return self.get_cached_row()

    def get_cached_row(self):
        data = self.get_unmapped_data()
        if not data:
            return
        return data[0]

    @cached_property
    def is_cached_fresh(self):
        return self.cached_row is not None and self.cached_row['expiry'] >= self.current_time

    def get_cached_data(self):
        """ Saved ratings that have not expired """
        if not self.is_cached_fresh:
            return
        return self.map_row(self.cached_row)

    @cached_property
    def cached_ratings(self):
        return self.get_cached_data()

    @cached_property
    def stale_ratings(self):
        return self.get_stale_ratings()

    def get_stale_ratings(self):
        """ Saved ratings that have expired """
        if self.cached_row is None or self.is_cached_fresh:
            return
        return self.map_row(self.cached_row)

    @cached_property
    def online_row(self):
        return self.get_online_row()

    def get_online_row(self):
        return dict(zip(self.keys, self.configure_mapped_data(self.online_data_mapped)))

    @cached_property
    def online_ratings(self):
        return self.map_row(self.online_row)

    @cached_property
    def ratings(self):
        return self.get_ratings()

    def get_ratings(self):
        if self.ratings_source is None:
            return {}
        return getattr(self, self.ratings_sources[self.ratings_source]) or {}

    @cached_property
    def ratings_source(self):
        return self.get_ratings_source()

    def get_ratings_source(self):
        """ Unexpired saved ratings, then expired ones when allowed, then online ratings.
        An empty online result falls back to expired ratings rather than replacing them """
        if not self.data_cond:
            return
        if self.cached_ratings:
            return 'cached'
        if self.allow_stale and self.stale_ratings:
            return 'stale'
        if self.online_ratings or not self.stale_ratings:
            return 'online'
        return 'stale'

    @property
    def is_stale(self):
        return self.ratings_source == 'stale'

    @property
    def is_unsaved(self):
        return self.ratings_source == 'online'

    @property
    def ratings_expiry(self):
        if self.is_unsaved:
            return self.online_row['expiry']
        return self.cached_row['expiry']

    def map_row(self, row):
        mapped_data = {}

        for k in row.keys():
            if k in ('id', 'expiry', 'provider_fingerprint'):
                continue

            v = row[k]

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
        """ Saving does not wait for item details: the placeholder row never replaces them """
        with self.connection.open():
            self.connection.open_connection.execute('BEGIN')
            self.set_or_update_null_cached_list_values('baseitem', self.placeholder_keys, self.placeholder_values)
            self.set_cached_list_values(self.table, self.keys, tuple(self.online_row.values()), overwrite=True)
            self.set_cached_deletion((self.item_id, ), self.deletion)  # Keep the item until its ratings expire
            self.connection.open_connection.execute('COMMIT')

    def try_cached_data(self, return_data=False):
        self.save_online_ratings()
        if not return_data:
            return
        return self.online_ratings


class RatingsSeasonsDict(RatingsDict):
    rating_attribs = (
        'provider_ratings',
    )

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
