"""Database connections that belong to the thread that opens them.

Each thread keeps at most one connection per database file. A thread's outermost
session opens the connection and explicitly closes it when the session ends; nested
sessions on the same thread borrow it. Connections never cross threads, which SQLite
enforces with check_same_thread.

Services and their small worker pools hold a session for their lifetime (DatabaseHold
and DatabaseWorkerPool). Other code opens a session for the work it does, and the
session closes its connection when that work completes.

Every statement enters a scope, so scopes are small classes rather than generator
context managers: commits run many statements while other threads compete for the GIL.
"""

from contextlib import ExitStack
from threading import local


class DatabaseThreadConnections(local):
    """The current thread's open connections by database file."""

    def __init__(self):
        self.connections = {}


class DatabaseSessionScope:
    """Borrow the thread's open connection, or own one until this scope exits."""

    def __init__(self, session):
        self.session = session
        self.connections = None
        self.connection = None
        self.is_owner = False

    def __enter__(self):
        self.connections = self.session.connections
        self.connection = self.connections.get(self.session.filename)
        if self.connection is None:
            self.connection = self.session.database.connect()
            self.connections[self.session.filename] = self.connection
            self.is_owner = True
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.is_owner:
            return
        del self.connections[self.session.filename]
        self.connection.close()


class DatabaseTransactionScope(DatabaseSessionScope):
    """Write atomically. A transaction already open on the connection is joined, and
    the outermost transaction commits, or rolls back when the scope raises."""

    is_outermost = False

    def __enter__(self):
        connection = super().__enter__()
        if connection.in_transaction:
            return connection
        try:
            connection.execute('BEGIN IMMEDIATE')
        except BaseException:
            super().__exit__(None, None, None)
            raise
        self.is_outermost = True
        return connection

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.is_outermost:
                self.end(exc_type)
        finally:
            super().__exit__(exc_type, exc_value, traceback)

    def end(self, exc_type):
        if exc_type is not None:
            self.rollback()
            return
        try:
            self.connection.execute('COMMIT')
        except BaseException:
            self.rollback()
            raise

    def rollback(self):
        """A failed COMMIT can leave the transaction open; a failed statement may not."""
        if self.connection.in_transaction:
            self.connection.execute('ROLLBACK')


class DatabaseSession:
    """Open, borrow and close the current thread's connection to one database."""

    thread_connections = DatabaseThreadConnections()

    def __init__(self, database):
        self.database = database
        self.filename = database._db_file

    @property
    def connections(self):
        return self.thread_connections.connections

    @property
    def connection(self):
        """The current thread's open connection to the database, or None."""
        return self.connections.get(self.filename)

    def open(self):
        """Borrow the thread's open connection, or own one until the scope exits."""
        return DatabaseSessionScope(self)

    def transaction(self):
        return DatabaseTransactionScope(self)


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
