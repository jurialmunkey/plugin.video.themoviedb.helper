from jurialmunkey.ftools import cached_property


class FindQueriesDatabaseTraktID:

    trakt_id_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
        },
        'item_type': {
            'data': 'TEXT',
            'indexed': True,
        },
        'query': {
            'data': 'TEXT',
            'indexed': True,
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
        },
        'tmdb_ep': {
            'data': 'INTEGER',
            'indexed': True,
        },
        'tvdb_id': {
            'data': 'INTEGER',
            'indexed': True,
        },
        'imdb_id': {
            'data': 'TEXT',
            'indexed': True,
        },
        'slug_id': {
            'data': 'TEXT',
            'indexed': True,
        },
        'trakt_id': {
            'data': 'INTEGER',
            'indexed': True,
        },
        'season': {
            'data': 'INTEGER',
            'indexed': True,
        },
        'episode': {
            'data': 'INTEGER',
            'indexed': True,
        },
    }

    """
    trakt_id
    """

    def get_trakt_id(self, id_value, id_type='tmdb', item_type=None, output_type='slug', season=None, episode=None):
        table = 'trakt_id'
        item_id = f'{id_type}_{id_value}_{item_type}'
        output_type = f'{output_type}_id'

        def get_kwgs():

            kwgs = (
                {
                    'values': (id_value, id_value, item_type, ),
                    'conditions': '(tmdb_id=? OR tmdb_ep=?) AND item_type=?'
                }
                if id_type == 'tmdb' and item_type == 'episode' else
                {
                    'values': (id_value, item_type, ),
                    'conditions': f'{id_type}_id=? AND item_type=?'
                }
            )

            if season is not None:
                kwgs['values'] = (*kwgs['values'], int(season))
                kwgs['conditions'] = f"{kwgs['conditions']} AND season=?"

            if episode is not None:
                kwgs['values'] = (*kwgs['values'], int(episode))
                kwgs['conditions'] = f"{kwgs['conditions']} AND episode=?"

            return kwgs

        def mapping_function(data):
            return data[0][output_type] if data and data[0] else None

        def get_cached():
            return self.get_cached_values(table, (output_type, ), mapping_function, **get_kwgs())

        def set_cached():
            if not self.is_expired(f'{table}.{item_id}'):
                return
            sync = GetTraktIDRequest(self.trakt_api, id_value, id_type)
            if not sync.values:
                return
            self.set_cached_values(table, sync.keys, sync.values, item_id=item_id)
            self.set_expiry(table)  # Also set table expiry since we might do a cross lookup
            return get_cached()

        return get_cached() or set_cached()


class GetTraktIDMovie:
    def __init__(self, meta):
        self.meta = meta

    item_type = 'movie'
    tmdb_type = 'movie'
    season = None
    episode = None
    tmdb_ep = None

    @staticmethod
    def get_value(dictionary, key):
        try:
            return dictionary[key]
        except (KeyError, TypeError, AttributeError):
            return

    @cached_property
    def item_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}'

    @cached_property
    def item_meta(self):
        return self.get_value(self.meta, self.item_type)

    @cached_property
    def item_meta_ids(self):
        return self.get_value(self.item_meta, 'ids')

    @cached_property
    def tmdb_id(self):
        return self.get_value(self.item_meta_ids, 'tmdb')

    @cached_property
    def tvdb_id(self):
        return self.get_value(self.item_meta_ids, 'tvdb')

    @cached_property
    def imdb_id(self):
        return self.get_value(self.item_meta_ids, 'imdb')

    @cached_property
    def trakt_id(self):
        return self.get_value(self.item_meta_ids, 'trakt')

    @cached_property
    def slug_id(self):
        return self.get_value(self.item_meta_ids, 'slug')

    @cached_property
    def query(self):
        query = self.get_value(self.item_meta, 'title') or ''
        query = query.casefold()
        return query

    @cached_property
    def item(self):
        return {
            'id': self.item_id,
            'item_type': self.item_type,
            'query': self.query,
            'tmdb_id': self.tmdb_id,
            'tmdb_ep': self.tmdb_ep,
            'tvdb_id': self.tvdb_id,
            'imdb_id': self.imdb_id,
            'slug_id': self.slug_id,
            'trakt_id': self.trakt_id,
            'season': self.season,
            'episode': self.episode,
        }


class GetTraktIDShow(GetTraktIDMovie):
    item_type = 'show'
    tmdb_type = 'tv'


class GetTraktIDEpisode(GetTraktIDShow):
    item_type = 'episode'
    tmdb_type = 'tv'

    @cached_property
    def item_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}.{self.season}.{self.episode}'

    @cached_property
    def show_meta(self):
        return self.get_value(self.meta, 'show')

    @cached_property
    def show_meta_ids(self):
        return self.get_value(self.show_meta, 'ids')

    @cached_property
    def tmdb_id(self):
        return self.get_value(self.show_meta_ids, 'tmdb')

    @cached_property
    def tmdb_ep(self):
        return self.get_value(self.item_meta_ids, 'tmdb')

    @cached_property
    def slug_id(self):
        return self.get_value(self.show_meta_ids, 'slug')

    @cached_property
    def season(self):
        return self.get_value(self.item_meta, 'season')

    @cached_property
    def episode(self):
        return self.get_value(self.item_meta, 'number')


def GetTraktIDFactory(item):
    routes = {
        'movie': GetTraktIDMovie,
        'show': GetTraktIDShow,
        'episode': GetTraktIDEpisode,
    }
    try:
        return routes[item['type']](item).item
    except KeyError:
        return


class GetTraktIDRequest:
    request_url = 'search/{id_type}/{id_value}'
    columns = FindQueriesDatabaseTraktID.trakt_id_columns

    def __init__(self, trakt_api, id_value, id_type='tmdb'):
        self.trakt_api = trakt_api
        self.id_value = id_value
        self.id_type = id_type

    @cached_property
    def url(self):
        return self.request_url.format(id_type=self.id_type, id_value=self.id_value)

    @cached_property
    def keys(self):
        return tuple(self.columns.keys())

    @cached_property
    def response(self):
        return self.trakt_api.get_response(self.url, limit=4095)

    @cached_property
    def response_json(self):
        return self.response.json() if self.response else None

    @cached_property
    def values(self):
        return [
            tuple([i[k] for k in self.keys])
            for i in self.items
        ]

    @cached_property
    def items(self):
        return [
            j for j in (
                GetTraktIDFactory(i)
                for i in self.response_json
            ) if j
        ] if self.response_json else []
