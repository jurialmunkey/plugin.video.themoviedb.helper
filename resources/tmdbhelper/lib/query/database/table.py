from tmdbhelper.lib.files.dbdata import DatabaseStatements
from collections import namedtuple


InsertStatement = namedtuple("InsertStatement", "statement table keys mapping")


class FindQueriesDatabaseTable:
    keys = ()  # SELECT keys
    table = ''  # FROM table
    conditions = ''  # WHERE conditions
    values = ()  # WHERE ?

    request_args = ()  # API method args
    request_kwgs = {}  # API method kwgs
    response_key = ''  # Key to get from API response to get data list

    expiry_id = ''  # Key to store expiry in main expiry table

    def __init__(self, parent):
        self.parent = parent

    @property
    def access(self):
        return self.parent.access

    @property
    def tmdb_api(self):
        return self.parent.tmdb_api

    @property
    def is_expired(self):
        return self.parent.is_expired

    @property
    def set_expiry(self):
        return self.parent.set_expiry

    @property
    def is_expired_get(self):
        return self.is_expired(self.expiry_id)

    @property
    def is_expired_set(self):
        return self.is_expired(self.expiry_id)

    @staticmethod
    def statement_mapping(i):
        return

    @property
    def insert_statements(self):
        return (
            InsertStatement(
                DatabaseStatements.insert_or_replace,  # Statement
                self.table,  # Table
                self.keys,  # Keys
                self.statement_mapping  # Mapping
            ),
        )

    @staticmethod
    def get_mapping(data):
        if not data:
            return
        return [{k: i[k] for k in i.keys()} for i in data]

    def set_tables(self, connection, statements, data):
        for i in data:
            for x, statement in enumerate(statements):
                connection.execute(statement, self.insert_statements[x].mapping(i))

    def get(self):
        data = None
        with self.access.connection.open():
            if not self.is_expired_get:
                data = self.parent.get_list_values(
                    self.table,
                    keys=self.keys,
                    values=self.values,
                    conditions=self.conditions)
        return self.get_mapping(data)

    def set(self):
        with self.access.connection.open():
            if not self.is_expired_set:
                return

        data = self.tmdb_api.get_response_json(*self.request_args, **self.request_kwgs)

        try:
            data = data[self.response_key] or {}
        except (KeyError, AttributeError, TypeError):
            return

        statements = [i.statement(i.table, i.keys) for i in self.insert_statements]

        with self.access.connection.open() as connection:
            connection.execute('BEGIN')
            self.set_tables(connection, statements, data)
            self.set_expiry(self.expiry_id)
            connection.execute('COMMIT')

        return self.get()

    def use(self):
        return self.get() or self.set()
