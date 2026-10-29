CALENDAR_DAY_COLUMNS = {
    'id': {'data': 'INTEGER PRIMARY KEY'},
    'date': {'data': 'TEXT NOT NULL', 'unique': True},
    'tmdb_type': {'data': 'TEXT NOT NULL', 'unique': True},
    'timezone': {'data': 'TEXT NOT NULL', 'unique': True},
    'language': {'data': 'TEXT NOT NULL', 'unique': True},
    'filters': {'data': 'TEXT NOT NULL', 'unique': True},
    'expiry': {'data': 'INTEGER NOT NULL'},
}

CALENDAR_ITEM_COLUMNS = {
    'day_id': {
        'data': 'INTEGER NOT NULL',
        'foreign_key': 'calendar_day(id)',
        'unique': True,
    },
    'tmdb_id': {'data': 'INTEGER NOT NULL', 'unique': True},
}
