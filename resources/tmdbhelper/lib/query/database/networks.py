from tmdbhelper.lib.query.database.daily_export import TableDailyExport


class FindQueriesDatabaseNetworks:

    networks_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
    }

    def get_networks_daily_export(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'networks'
        daily_export.keys = ('id', 'name', )
        daily_export.export_list = 'tv_network'
        return daily_export

    def get_networks(self, limit=250, page=1):
        daily_export = self.get_networks_daily_export()
        daily_export.conditions = f'name IS NOT NULL ORDER BY id LIMIT {limit}'
        daily_export.conditions = f'{daily_export.conditions} OFFSET {((limit * page) - limit)}'
        return daily_export.get_cached() or daily_export.set_cached()

    def get_network(self, query):
        daily_export = self.get_networks_daily_export()
        daily_export.conditions = f'name LIKE "%{query}%" ORDER BY name'
        return daily_export.get_cached() or daily_export.set_cached()
