"""Schema, queries, and persistence for the standalone collection index."""
from datetime import datetime, timedelta
from pathlib import Path
from tmdbhelper.lib.collections.refresh import CollectionRefreshPolicy
import sqlite3


DATABASE_PATH = Path(__file__).resolve().parents[3] / 'databases' / 'collections.db'
DATABASE_VERSION = 1
DATABASE_SCHEMA = '''
    CREATE TABLE collection (
        collection_id INTEGER PRIMARY KEY,
        discovered_at TEXT NOT NULL,
        last_checked_at TEXT,
        last_attempted_at TEXT,
        retry_after TEXT,
        failure_count INTEGER NOT NULL DEFAULT 0,
        last_status INTEGER,
        active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
    );
    CREATE TABLE collection_movie (
        collection_id INTEGER NOT NULL REFERENCES collection (collection_id) ON DELETE CASCADE,
        movie_id INTEGER NOT NULL,
        release_date TEXT,
        PRIMARY KEY (collection_id, movie_id)
    ) WITHOUT ROWID;
    CREATE INDEX collection_movie_id ON collection_movie (movie_id);
    CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
'''


class CollectionDatabase:
    def __init__(self, connection):
        self.connection = connection
        self.connection.execute('PRAGMA foreign_keys=ON')

    def initialise(self):
        version = self.get_version()
        if version == DATABASE_VERSION:
            return
        if version != 0 or self.connection.execute('SELECT name FROM sqlite_master').fetchone():
            raise ValueError(f'Unsupported collection database version: {version}')
        self.connection.executescript(DATABASE_SCHEMA)
        self.connection.execute(f'PRAGMA user_version={DATABASE_VERSION}')

    def get_version(self):
        return self.connection.execute('PRAGMA user_version').fetchone()[0]

    def get_metadata(self, key):
        row = self.connection.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()
        return row[0] if row else None

    def set_metadata(self, values):
        self.connection.executemany(
            'INSERT INTO metadata (key, value) VALUES (?, ?) '
            'ON CONFLICT (key) DO UPDATE SET value=excluded.value',
            ((key, str(value)) for key, value in values.items()))

    def delete_metadata(self, keys):
        placeholders = ','.join('?' for key in keys)
        self.connection.execute(f'DELETE FROM metadata WHERE key IN ({placeholders})', keys)

    def set_snapshot(self, identifiers, snapshot_date, digest):
        previous = self.get_metadata('snapshot_date')
        if previous and snapshot_date < previous:
            raise ValueError('Cannot update the index using an older collection-ID export')
        with self.connection:
            self.connection.execute('UPDATE collection SET active=0')
            self.connection.executemany(
                'INSERT INTO collection (collection_id, discovered_at) VALUES (?, ?) '
                'ON CONFLICT (collection_id) DO UPDATE SET active=1',
                ((identifier, snapshot_date) for identifier in identifiers))
            self.set_metadata({'snapshot_date': snapshot_date, 'snapshot_sha256': digest})

    def get_collections(self):
        rows = self.connection.execute(
            'SELECT collection_id, last_checked_at, last_attempted_at, retry_after, last_status '
            'FROM collection WHERE active=1 ORDER BY collection_id').fetchall()
        dates = {}
        for collection_id, release_date in self.connection.execute(
                'SELECT collection_id, release_date FROM collection_movie ORDER BY collection_id, movie_id'):
            dates.setdefault(collection_id, []).append(release_date)
        return [
            dict(
                collection_id=row[0], last_checked_at=row[1], last_attempted_at=row[2],
                retry_after=row[3], last_status=row[4], release_dates=dates.get(row[0], []))
            for row in rows
        ]

    def get_queue(self, started_at, now, due_only=False):
        policy = CollectionRefreshPolicy()
        entries = [
            entry for entry in self.get_collections()
            if not entry['retry_after'] or entry['retry_after'] <= now.isoformat(timespec='seconds')
        ]
        pending = [entry for entry in entries if entry['last_checked_at'] is None]
        existing = [entry for entry in entries if entry['last_checked_at'] is not None]
        refreshes = [
            (policy.get_next_check(entry['last_checked_at'], entry['release_dates'], now.date()), entry)
            for entry in existing
            if entry['last_status'] != 200 or not entry['last_attempted_at'] or entry['last_attempted_at'] < started_at
        ]
        refreshes = sorted(
            (due, entry['collection_id']) for due, entry in refreshes
            if not due_only or due <= now.date())
        return [entry['collection_id'] for entry in pending] + [identifier for due, identifier in refreshes]

    def set_collection(self, collection_id, movies, checked_at):
        with self.connection:
            self.connection.execute('DELETE FROM collection_movie WHERE collection_id=?', (collection_id,))
            self.connection.executemany(
                'INSERT INTO collection_movie (collection_id, movie_id, release_date) VALUES (?, ?, ?)',
                ((collection_id, movie_id, release_date) for movie_id, release_date in movies))
            self.connection.execute(
                'UPDATE collection SET last_checked_at=?, last_attempted_at=?, last_status=200, '
                'retry_after=NULL, failure_count=0 WHERE collection_id=?',
                (checked_at, checked_at, collection_id))

    def set_failure(self, collection_id, attempted_at, status):
        failures = self.connection.execute(
            'SELECT failure_count FROM collection WHERE collection_id=?', (collection_id,)).fetchone()[0] + 1
        delay = timedelta(days=7) if status == 404 else timedelta(hours=min(24, 2 ** min(failures - 1, 5)))
        retry_after = (datetime.fromisoformat(attempted_at) + delay).isoformat(timespec='seconds')
        with self.connection:
            self.connection.execute(
                'UPDATE collection SET last_attempted_at=?, last_status=?, retry_after=?, failure_count=? '
                'WHERE collection_id=?',
                (attempted_at, status or 0, retry_after, failures, collection_id))

    def get_counts(self):
        rows = self.connection.execute(
            '''
            SELECT 'collections', COUNT(*) FROM collection WHERE active=1
            UNION ALL SELECT 'populated', COUNT(*) FROM collection WHERE active=1 AND last_checked_at IS NOT NULL
            UNION ALL SELECT 'unavailable', COUNT(*) FROM collection WHERE active=1 AND last_status=404
            UNION ALL SELECT 'unresolved', COUNT(*) FROM collection
                WHERE active=1 AND (last_status IS NULL OR last_status NOT IN (200, 404))
            UNION ALL SELECT 'memberships', COUNT(*) FROM collection_movie
                JOIN collection USING (collection_id) WHERE active=1
            UNION ALL SELECT 'movies', COUNT(DISTINCT movie_id) FROM collection_movie
                JOIN collection USING (collection_id) WHERE active=1
            ''').fetchall()
        return dict(rows)

    def validate(self):
        if self.connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise sqlite3.DatabaseError('Collection database integrity check failed')
        if self.connection.execute('PRAGMA foreign_key_check').fetchall():
            raise sqlite3.DatabaseError('Collection database foreign key check failed')

    def compact(self):
        self.connection.execute('VACUUM')
