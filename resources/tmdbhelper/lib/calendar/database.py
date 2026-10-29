from contextlib import closing
from tmdbhelper.lib.calendar.tabledef import CALENDAR_DAY_COLUMNS, CALENDAR_ITEM_COLUMNS
from tmdbhelper.lib.files.dbdata import Database


class CalendarDatabase(Database):
    cache_filename = 'Calendar.db'
    database_version = 1
    day_conditions = 'date=? AND tmdb_type=? AND timezone=? AND language=? AND filters=?'

    def __init__(self):
        super().__init__(filename=self.cache_filename)

    @property
    def database_tables(self):
        return {'calendar_day': CALENDAR_DAY_COLUMNS, 'calendar_item': CALENDAR_ITEM_COLUMNS}

    def get_day(self, date, tmdb_type, timezone, language, filters, current_time):
        rows = self.get_list_values(
            'calendar_day', keys=('id', ),
            values=(date, tmdb_type, timezone, language, filters, current_time),
            conditions=f'{self.day_conditions} AND expiry>?')
        if not rows:
            return None
        items = self.get_list_values(
            'calendar_item', keys=('tmdb_id', ), values=(rows[0]['id'], ), conditions='day_id=?')
        return [item['tmdb_id'] for item in items]

    def set_day(self, date, tmdb_type, timezone, language, filters, expiry, items):
        with closing(self.get_database()) as connection:
            with connection:
                self.write_day(connection, date, tmdb_type, timezone, language, filters, expiry, items)

    def write_day(self, connection, date, tmdb_type, timezone, language, filters, expiry, items):
        values = (date, tmdb_type, timezone, language, filters)
        connection.execute(
            'INSERT OR IGNORE INTO calendar_day(date, tmdb_type, timezone, language, filters, expiry) '
            'VALUES (?, ?, ?, ?, ?, ?)', (*values, expiry))
        day_id = connection.execute(
            f'SELECT id FROM calendar_day WHERE {self.day_conditions}', values).fetchone()[0]
        connection.execute('UPDATE calendar_day SET expiry=? WHERE id=?', (expiry, day_id))
        connection.execute('DELETE FROM calendar_item WHERE day_id=?', (day_id, ))
        connection.executemany(
            'INSERT INTO calendar_item(day_id, tmdb_id) VALUES (?, ?)',
            [(day_id, tmdb_id) for tmdb_id in set(items)])

    def get_days(self, tmdb_type, timezone, language, filters, start_date, end_date, current_time):
        return self.get_list_values(
            'calendar_item INNER JOIN calendar_day ON calendar_day.id=calendar_item.day_id',
            keys=('calendar_item.tmdb_id AS id', 'calendar_day.date AS calendar_date'),
            values=(tmdb_type, timezone, language, filters, start_date, end_date, current_time),
            conditions=(
                'tmdb_type=? AND timezone=? AND language=? AND filters=? '
                'AND date>=? AND date<? AND expiry>? ORDER BY date, tmdb_id')) or []
