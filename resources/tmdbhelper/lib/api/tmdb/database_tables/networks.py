from tmdbhelper.lib.api.tmdb.database_tables.collections import TableDailyExport


class TMDbDatabaseNetworks:

    networks_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
    }

    def get_networks(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'networks'
        daily_export.keys = ('id', 'name', )
        daily_export.export_list = 'tv_network'
        daily_export.conditions = 'name IS NOT NULL ORDER BY id'
        return daily_export.get_cached() or daily_export.set_cached()
