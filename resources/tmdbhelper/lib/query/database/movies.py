from tmdbhelper.lib.query.database.daily_export import TableDailyExport


class FindQueriesDatabaseMovies:

    movies_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'original_title': {
            'data': 'TEXT'
        },
        'popularity': {
            'data': 'REAL'
        },
    }

    def get_movies(self, limit=20, page=1):
        daily_export = TableDailyExport(self)
        daily_export.table = 'movies'
        daily_export.keys = ('id', 'original_title', 'popularity')
        daily_export.mappings = ('id', 'original_title', 'popularity')
        daily_export.export_list = 'movie'
        daily_export.conditions = f'original_title IS NOT NULL ORDER BY popularity DESC LIMIT {limit}'
        daily_export.conditions = f'{daily_export.conditions} OFFSET {((limit * page) - limit)}'
        return daily_export.get_cached() or daily_export.set_cached()
