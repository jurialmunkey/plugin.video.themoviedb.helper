from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings
from jurialmunkey.parser import try_int


class RatingsDict(BaseList):
    expiry_time = 7 * 86400
    cached_data_table = table = 'ratings'
    cached_data_conditions = 'id=? AND expiry>=?'

    rating_attribs = (
        'omdb_ratings',
        'provider_ratings',
        'tmdb_ratings',
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
        """ WHERE condition ? ? ? ? = value, value, value, value """
        return (self.item_id, self.current_time, )

    @cached_property
    def mediatype(self):
        return self.get_mediatype()

    @cached_property
    def trakt_type(self):
        return self.get_trakt_type()

    @cached_property
    def imdb_id(self):
        return self.get_imdb_id()

    @cached_property
    def imdb_top250_list(self):
        return self.get_imdb_top250_list()

    def get_mediatype(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type == 'tv':
            return 'tvshow'

    def get_trakt_type(self):
        if self.tmdb_type == 'movie':
            return 'movie'
        if self.tmdb_type == 'tv':
            return 'show'

    def get_imdb_id(self):
        return FindQueriesDatabase().get_trakt_id(self.tmdb_id, 'tmdb', self.trakt_type, 'imdb')

    def get_imdb_top250_list(self):
        return FindQueriesDatabase().get_imdb_top250_list_cached(self.tmdb_type)

    @cached_property
    def ratings_suppliers(self):
        return self.get_ratings_suppliers()

    def get_ratings_suppliers(self):
        providers = RatingsProviderSettings().get_enabled_providers(self.mediatype)
        return tuple(
            provider.ratings_classes[self.mediatype](
                provider=provider, tmdb_type=self.tmdb_type, tmdb_id=self.tmdb_id,
                imdb_id=self.imdb_id, season=self.season, episode=self.episode)
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
        try:
            return {'top250': self.imdb_top250_list.index(try_int(self.tmdb_id)) + 1}  # Must be an int to match
        except (KeyError, TypeError, IndexError, ValueError):
            return {}

    @cached_property
    def omdb_ratings(self):
        if not self.common_apis.omdb_api or not self.imdb_id:
            return {}
        try:
            return self.common_apis.omdb_api.get_ratings_awards(imdb_id=self.imdb_id) or {}
        except (KeyError, TypeError, IndexError, ValueError):
            return {}

    @cached_property
    def tmdb_ratings(self):
        data = self.common_apis.tmdb_api.get_response_json(self.tmdb_type, self.tmdb_id)
        if not data:
            return {}
        try:
            return {
                'tmdb_rating': int(data['vote_average'] * 10),
                'tmdb_votes': data['vote_count']
            }
        except (KeyError, TypeError, IndexError, ValueError):
            return {}

    @cached_property
    def online_data_mapped(self):
        return self.get_online_data_mapped()

    def get_online_data_mapped(self):
        """ function called when local cache does not have any data """

        def get_data_attr(attr):
            data = getattr(self, attr)
            return data or {}

        # precache some property values before threading
        for attr in ('mediatype', 'trakt_type', 'imdb_id', 'ratings_suppliers'):
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
            try:
                return data[k]
            except (TypeError, KeyError, IndexError, ValueError):
                return
        return [get_value(k) for k in self.keys]

    def get_cached_data(self):
        data = self.get_unmapped_data()
        if not data:
            return

        mapped_data = {}

        for k in data[0].keys():
            if k in ('id', 'expiry'):
                continue

            v = data[0][k]

            if v in (None, ''):
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

    def try_cached_data(self, return_data=False):
        if not self.parent_item_data:
            return
        if not self.online_data_mapped:
            return

        func = self.set_cached_values
        args = (self.table, self.item_id, self.keys)
        kwgs = {'values': self.configure_mapped_data(self.online_data_mapped)}

        with self.connection.open():
            self.connection.open_connection.execute('BEGIN')
            func(*args, **kwgs)
            self.connection.open_connection.execute('COMMIT')

        if not return_data:
            return
        return self.get_cached_data()


class RatingsSeasonsDict(RatingsDict):
    rating_attribs = (
        'provider_ratings',
    )

    def get_mediatype(self):
        return 'season'

    def get_trakt_type(self):
        return 'show'

    def get_online_data_mapped(self):
        if self.season is None:
            return
        if self.tmdb_type != 'tv':
            return
        return super().get_online_data_mapped()

    @property
    def item_id(self):
        return self.get_season_id(self.tmdb_type, self.tmdb_id, self.season)


class RatingsEpisodesDict(RatingsSeasonsDict):
    def get_mediatype(self):
        return 'episode'

    def get_online_data_mapped(self):
        if self.episode is None:
            return
        return super().get_online_data_mapped()

    @property
    def item_id(self):
        return self.get_episode_id(self.tmdb_type, self.tmdb_id, self.season, self.episode)
