from tmdbhelper.lib.files.dbdata import DatabaseStatements
from tmdbhelper.lib.query.database.table import InsertStatement, FindQueriesDatabaseTable


class FindQueriesDatabaseTableWatchProviders(FindQueriesDatabaseTable):
    table = 'watch_providers INNER JOIN watch_providers_details ON watch_providers_details.provider_id = watch_providers.provider_id'
    keys = ('iso_country', 'tmdb_type', 'watch_providers.provider_id', 'provider_name', 'logo_path', 'display_priority')
    conditions = 'iso_country=? AND tmdb_type=? ORDER BY display_priority'
    response_key = 'results'

    @property
    def values(self):
        return (self.iso_country, self.tmdb_type, )

    @property
    def expiry_id(self):
        return f'watch_providers.{self.tmdb_type}.{self.iso_country}'

    @property
    def request_args(self):
        return ('watch', 'providers', self.tmdb_type)

    @property
    def request_kwgs(self):
        return {'watch_region': self.iso_country}

    def get_statement_watch_providers(self, i):
        return (
            self.iso_country,
            self.tmdb_type,
            i['provider_id'],
        )

    @staticmethod
    def get_statement_watch_providers_details(i):
        return (
            i['provider_id'],
            i['provider_name'],
            i['logo_path'],
            i['display_priority']
        )

    @property
    def insert_statements(self):
        return (
            InsertStatement(
                DatabaseStatements.insert_or_replace,  # Statement
                'watch_providers',  # Table
                ('iso_country', 'tmdb_type', 'provider_id'),  # Keys
                self.get_statement_watch_providers  # Mapping
            ),
            InsertStatement(
                DatabaseStatements.insert_or_replace,  # Statement
                'watch_providers_details',  # Table
                ('provider_id', 'provider_name', 'logo_path', 'display_priority'),  # Keys
                self.get_statement_watch_providers_details  # Mapping
            ),
        )


class FindQueriesDatabaseWatchProviders:
    watch_providers_columns = {
        'iso_country': {
            'data': 'TEXT',
            'indexed': True,
            'unique': True
        },
        'tmdb_type': {
            'data': 'TEXT',
            'unique': True
        },
        'provider_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
    }

    watch_providers_details_columns = {
        'provider_id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True,
            'unique': True,
            'foreign_key': 'watch_providers_details(provider_id)',
        },
        'provider_name': {
            'data': 'TEXT'
        },
        'logo_path': {
            'data': 'TEXT'
        },
        'display_priority': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    """
    certification
    """

    @staticmethod
    def get_provider_allowlist():
        from tmdbhelper.lib.addon.plugin import get_setting
        provider_allowlist = get_setting('provider_allowlist', 'str')
        provider_allowlist = provider_allowlist.split(' | ') if provider_allowlist else []
        provider_allowlist = [f"'{i}'" for i in provider_allowlist]
        provider_allowlist = ', '.join(provider_allowlist)
        provider_allowlist = f'provider_name IN ({provider_allowlist}) AND ' if provider_allowlist else ''
        return provider_allowlist

    def get_watch_providers(self, tmdb_type, iso_country, allowlist_only=False):
        database_table = FindQueriesDatabaseTableWatchProviders(self)
        database_table.tmdb_type = tmdb_type
        database_table.iso_country = iso_country
        database_table.conditions = f'{self.get_provider_allowlist()}{database_table.conditions}' if allowlist_only else database_table.conditions
        return database_table.use()
