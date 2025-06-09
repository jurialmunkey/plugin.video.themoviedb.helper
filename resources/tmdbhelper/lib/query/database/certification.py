from tmdbhelper.lib.query.database.table import FindQueriesDatabaseTable


class FindQueriesDatabaseTableCertification(FindQueriesDatabaseTable):
    table = 'certification'
    keys = ('iso_country', 'certification', 'tmdb_type', 'meaning', 'ordering')
    response_key = 'certifications'

    @property
    def conditions(self):
        if not self.iso_country:
            return 'tmdb_type=? ORDER BY ordering'
        return 'iso_country=? AND tmdb_type=? ORDER BY ordering'

    @property
    def values(self):
        if not self.iso_country:
            return (self.tmdb_type, )
        return (self.iso_country, self.tmdb_type)

    @property
    def expiry_id(self):
        return f'{self.table}.{self.tmdb_type}'

    @property
    def request_args(self):
        return ('certification', self.tmdb_type, 'list')

    request_kwgs = {}

    def statement_mapping(self, i, iso_country):
        return (
            iso_country,
            i['certification'],
            self.tmdb_type,
            i['meaning'],
            i['order']
        )

    def set_tables(self, connection, statements, data):
        for iso_country, v in data.items():
            for i in v:
                for x, statement in enumerate(statements):
                    connection.execute(statement, self.insert_statements[x].mapping(i, iso_country))


class FindQueriesDatabaseCertification:
    certification_columns = {
        'iso_country': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'certification': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'tmdb_type': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'meaning': {
            'data': 'TEXT'
        },
        'ordering': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    """
    certification
    """

    def get_certification(self, tmdb_type, iso_country=None):
        database_table = FindQueriesDatabaseTableCertification(self)
        database_table.tmdb_type = tmdb_type
        database_table.iso_country = iso_country
        return database_table.use()
