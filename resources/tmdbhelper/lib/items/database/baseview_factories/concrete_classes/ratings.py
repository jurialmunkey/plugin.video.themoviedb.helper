from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.baseview_factories.concrete_classes.baseclass import BaseList
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.addon.thread import ParallelThread
from jurialmunkey.parser import try_int


class RatingsDict(BaseList):
    expiry_time = 7 * 86400
    cached_data_table = table = 'ratings'
    cached_data_conditions = 'id=? AND expiry>=?'

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
    def mdblist_ratings(self):
        if not self.common_apis.mdblist_api:
            return {}
        return self.common_apis.mdblist_api.get_ratings(self.trakt_type, self.tmdb_id) or {}

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
    def trakt_ratings(self):
        if not self.common_apis.trakt_api or not self.common_apis.trakt_api.authenticator.is_authorized or not self.imdb_id:
            return {}
        data = self.common_apis.trakt_api.get_response_json(f'{self.trakt_type}s/{self.imdb_id}/ratings')
        if not data:
            return {}
        try:
            return {
                'trakt_rating': int(float(data['rating']) * 10),  # Convert /10 float to /100 int
                'trakt_votes': int(data['votes']),
            }
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
        """ function called when local cache does not have any data """
        data = {}

        def get_data_attr(attr):
            data.update(getattr(self, attr))

        attribs = (
            'omdb_ratings',
            'mdblist_ratings',
            'trakt_ratings',
            'tmdb_ratings',
            'imdb_top250',
        )

        self.mediatype = self.get_mediatype()
        self.trakt_type = self.get_trakt_type()
        self.imdb_id = self.get_imdb_id()

        with ParallelThread(attribs, get_data_attr):
            pass

        return data

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

        ratings_style = {
            'tmdb_rating': lambda v: f'{(v / 10):.1f}',
            'trakt_rating': lambda v: f'{(v / 10):.1f}',
            'imdb_rating': lambda v: f'{(v / 10):.1f}',
            'letterboxd_rating': lambda v: f'{(v / 20):.1f}',  # 5 Star rating
            'rogerebert_rating': lambda v: f'{(v / 25):.1f}',  # 4 Star rating
        }

        mapped_data = {}

        for k in data[0].keys():
            if k in ('id', 'expiry'):
                continue

            v = data[0][k]

            if not v:
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
                mapped_data[k] = ratings_style[k](v)
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
