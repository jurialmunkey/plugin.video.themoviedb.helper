"""Profile-local collection drop preferences, separate from the shared index."""
from contextlib import closing, contextmanager
from pathlib import Path
import sqlite3


class CollectionDropStore:
    def __init__(self, filename):
        self.filename = Path(filename)

    @contextmanager
    def open(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.filename, timeout=30)) as connection, connection:
            self.initialise(connection)
            yield connection

    @staticmethod
    def initialise(connection):
        connection.execute(
            'CREATE TABLE IF NOT EXISTS collection_drop ('
            'collection_id INTEGER PRIMARY KEY CHECK (collection_id>0), dropped_at TEXT NOT NULL)')

    def get_drops(self):
        with self.open() as connection:
            return dict(connection.execute('SELECT collection_id, dropped_at FROM collection_drop').fetchall())

    def drop(self, collection_id, dropped_at):
        with self.open() as connection:
            connection.execute(
                'INSERT INTO collection_drop (collection_id, dropped_at) VALUES (?, ?) '
                'ON CONFLICT (collection_id) DO UPDATE SET dropped_at=excluded.dropped_at',
                (collection_id, dropped_at))

    def remove(self, drops):
        # A render using an older snapshot must not erase a more recent drop.
        with self.open() as connection:
            connection.executemany(
                'DELETE FROM collection_drop WHERE collection_id=? AND dropped_at=?', drops.items())


def get_collection_drop_store():
    from xbmcvfs import translatePath
    from tmdbhelper.lib.addon.plugin import ADDONDATA
    return CollectionDropStore(translatePath(f'{ADDONDATA}sync/collection_drops.db'))
