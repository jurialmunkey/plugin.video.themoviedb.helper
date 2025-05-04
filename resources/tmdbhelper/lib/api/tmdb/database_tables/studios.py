from tmdbhelper.lib.api.tmdb.database_tables.collections import TableDailyExport


class TMDbDatabaseStudios:

    studios_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
    }

    def get_studios(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'studios'
        daily_export.keys = ('id', 'name', )
        daily_export.export_list = 'production_company'
        daily_export.conditions = 'name IS NOT NULL ORDER BY id'
        return daily_export.get_cached() or daily_export.set_cached()
