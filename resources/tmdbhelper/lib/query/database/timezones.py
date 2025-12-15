from tmdbhelper.lib.query.database.table import FindQueriesDatabaseTable


class FindQueriesDatabaseTableTimezones(FindQueriesDatabaseTable):
    table = 'timezones'
    keys = ('iso_country', 'timezone', )
    response_key = ''

    @property
    def conditions(self):
        if not self.iso_country:
            return 'iso_country IS NOT NULL ORDER BY iso_country, timezone'
        return 'iso_country=? ORDER BY timezone'

    @property
    def values(self):
        if not self.iso_country:
            return ()
        return (self.iso_country, )

    @property
    def expiry_id(self):
        return f'{self.table}'

    @property
    def request_args(self):
        return ('configuration', 'timezones')

    request_kwgs = {}

    def statement_mapping(self, timezone, iso_country):
        return (
            iso_country,
            timezone,
        )

    def set_tables(self, connection, statements, data):
        for item in data:
            iso_country = item['iso_3166_1']
            for timezone in item['zones']:
                for x, statement in enumerate(statements):
                    connection.execute(statement, self.insert_statements[x].mapping(timezone, iso_country))


class FindQueriesDatabaseTimezones:
    timezones_columns = {
        'iso_country': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'timezone': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
    }

    """
    timezones
    """

    def get_timezones(self, iso_country=None):
        database_table = FindQueriesDatabaseTableTimezones(self)
        database_table.iso_country = iso_country
        return database_table.use()
