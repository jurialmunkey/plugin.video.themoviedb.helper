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

    @staticmethod
    def map_stats(data):
        return {f"{item['name']}_{item['type']}": item['stat'] for item in data}

    def get_trakt_stats(self, forced=False):
        from tmdbhelper.lib.sync.providers.stats import Stats
        supplier = Stats()
        if supplier.provider is None:
            return
        if not forced:
            data = self.get_cached_values('trakt_stats', ('name', 'type', 'stat'))
            if data is not None:
                return self.map_stats(data)
        items = supplier.items
        if items is None:
            return
        self.set_stats_snapshot(items)
        return self.map_stats(items)

    def set_stats_snapshot(self, items):
        keys = tuple(self.trakt_stats_columns)
        values = [tuple(item[key] for key in keys) for item in items]
        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            self.del_list_values('trakt_stats', conditions='1=1', connection=connection)
            self.access.set_cached_list_values('trakt_stats', keys, values)
            self.set_expiry('trakt_stats', expiry=1200)
            connection.execute('COMMIT')

    def invalidate_stats(self):
        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            items = self.get_all_values('trakt_stats', ('name', 'type', 'stat'))
            self.del_list_values('trakt_stats', conditions='1=1', connection=connection)
            self.access.del_cached('expiry', 'trakt_stats')
            connection.execute('COMMIT')
        return self.map_stats(items)
