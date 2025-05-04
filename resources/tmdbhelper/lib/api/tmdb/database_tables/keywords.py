from tmdbhelper.lib.api.tmdb.database_tables.collections import TableDailyExport


class TMDbDatabaseKeywords:

    keywords_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
    }

    def get_keywords(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'keywords'
        daily_export.keys = ('id', 'name', )
        daily_export.export_list = 'keyword'
        daily_export.conditions = 'name IS NOT NULL ORDER BY id'
        return daily_export.get_cached() or daily_export.set_cached()
