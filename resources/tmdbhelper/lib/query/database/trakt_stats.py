from jurialmunkey.ftools import cached_property


class FindQueriesDatabaseTraktStats:

    trakt_stats_columns = {
        'name': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True,
        },
        'type': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True,
        },
        'stat': {
            'data': 'INTEGER',
        },
    }

    """
    trakt_stats
    """

    def get_trakt_stats(self):
        table = 'trakt_stats'

        def mapping_function(data):
            return {f"{i['name']}_{i['type']}": i['stat'] for i in data} if data else {}

        def get_cached():
            # kwgs = {'values': (id_value, item_type, ), 'conditions': f'{id_type}=? AND item_type=?'}
            kwgs = {}
            keys = ('name', 'type', 'stat', )
            return self.get_cached_values(table, keys, mapping_function, **kwgs)

        def set_cached():
            if not self.trakt_api.is_authorized:
                return
            sync = GetTraktStatsRequest(self.trakt_api)
            if not sync.values:
                return
            self.set_cached_values(table, sync.keys, sync.values, expiry=1200)  # Cache for 20 minutes
            return get_cached()

        return get_cached() or set_cached()


class GetTraktStatsRequest:
    url = 'users/me/stats'

    def __init__(self, trakt_api):
        self.trakt_api = trakt_api

    @cached_property
    def keys(self):
        return tuple(FindQueriesDatabaseTraktStats.trakt_stats_columns.keys())

    @cached_property
    def response_json(self):
        response = self.trakt_api.get_response(self.url)
        return response.json() if response else None

    @cached_property
    def values(self):
        return [
            tuple([i[k] for k in self.keys])
            for i in self.items
        ]

    @cached_property
    def items(self):
        return [
            {
                'name': item_k,
                'type': base_k,
                'stat': item_v,
            }
            for base_k, base_v in self.response_json.items()
            for item_k, item_v in base_v.items()
            if isinstance(item_v, int)
        ] if self.response_json else []
