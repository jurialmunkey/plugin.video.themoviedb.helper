from tmdbhelper.lib.query.database.daily_export import TableDailyExport


class FindQueriesDatabaseTvshows:

    tvshows_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'original_name': {
            'data': 'TEXT'
        },
        'popularity': {
            'data': 'REAL'
        },
    }

    def get_tvshows(self, limit=20, page=1):
        daily_export = TableDailyExport(self)
        daily_export.table = 'tvshows'
        daily_export.keys = ('id', 'original_name', 'popularity')
        daily_export.mappings = ('id', 'original_name', 'popularity')
        daily_export.export_list = 'tv_series'
        daily_export.conditions = f'original_name IS NOT NULL ORDER BY popularity DESC LIMIT {limit}'
        daily_export.conditions = f'{daily_export.conditions} OFFSET {((limit * page) - limit)}'
        return daily_export.get_cached() or daily_export.set_cached()
