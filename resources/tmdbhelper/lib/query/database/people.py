from tmdbhelper.lib.query.database.daily_export import TableDailyExport


class FindQueriesDatabasePeople:

    people_columns = {
        'id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT'
        },
        'popularity': {
            'data': 'REAL'
        },
    }

    @property
    def people_daily_export(self):
        daily_export = TableDailyExport(self)
        daily_export.table = 'people'
        daily_export.keys = ('id', 'name', 'popularity')
        daily_export.export_list = 'person'
        return daily_export

    def get_people(self, limit=20, page=1):
        daily_export = self.people_daily_export
        daily_export.conditions = f'name IS NOT NULL ORDER BY popularity DESC LIMIT {limit}'
        daily_export.conditions = f'{daily_export.conditions} OFFSET {((limit * page) - limit)}'
        return daily_export.get_cached() or daily_export.set_cached()

    def get_person_by_id(self, tmdb_id):
        daily_export = self.people_daily_export
        daily_export.conditions = f'id={tmdb_id}'
        value = daily_export.get_cached() or daily_export.set_cached()
        if not value:
            return
        return value[0]['name']
