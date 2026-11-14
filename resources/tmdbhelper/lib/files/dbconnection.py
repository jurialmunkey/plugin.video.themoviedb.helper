"""Database connections that belong to the thread that opens them.

Each thread keeps at most one connection per database file. A thread's outermost
session opens the connection and explicitly closes it when the session ends; nested
sessions on the same thread borrow it. Connections never cross threads, which SQLite
enforces with check_same_thread.

Services and their small worker pools hold a session for their lifetime (DatabaseHold
and DatabaseWorkerPool). Other code opens a session for the work it does, and the
session closes its connection when that work completes.
"""

from contextlib import ExitStack, contextmanager
from threading import local


class DatabaseThreadConnections(local):
    """The current thread's open connections by database file."""

    def __init__(self):
        self.connections = {}


class DatabaseSession:
    """Open, borrow and close the current thread's connection to one database."""

    thread_connections = DatabaseThreadConnections()

    def __init__(self, database):
        self.database = database

    @property
    def connections(self):
        return self.thread_connections.connections

    @property
    def filename(self):
        return self.database._db_file

    @property
    def connection(self):
        """The current thread's open connection to the database, or None."""
        return self.connections.get(self.filename)

    @contextmanager
    def open(self):
        """Borrow the thread's open connection, or own one until this scope ends."""
        connection = self.connection
        if connection is not None:
            yield connection
            return
        with self.owned() as connection:
            yield connection

    @contextmanager
    def owned(self):
        connection = self.database.connect()
        self.connections[self.filename] = connection
        try:
            yield connection
        finally:
            del self.connections[self.filename]
            connection.close()

    @contextmanager
    def transaction(self):
        """Write atomically. A transaction already open on the connection is joined, and
        the outermost transaction commits, or rolls back when the scope raises."""
        with self.open() as connection:
            if connection.in_transaction:
                yield connection
                return
            connection.execute('BEGIN IMMEDIATE')
            try:
                yield connection
                connection.execute('COMMIT')
            except BaseException:
                self.rollback(connection)
                raise

    @staticmethod
    def rollback(connection):
        """A failed COMMIT can leave the transaction open; a failed statement may not."""
        if connection.in_transaction:
            connection.execute('ROLLBACK')


class DatabaseHold:
    """Keep the current thread's connections to the databases open until the hold ends.

    Owners hold their connections for their lifetime, so that every database access on
    their thread reuses them. Exiting closes them on the same thread.
    """

    def __init__(self, *databases):
        self.databases = databases
        self.sessions = None

    def __enter__(self):
        with ExitStack() as sessions:
            for database in self.databases:
                sessions.enter_context(database.session())
            self.sessions = sessions.pop_all()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sessions, self.sessions = self.sessions, None
        return sessions.__exit__(exc_type, exc_value, traceback)
