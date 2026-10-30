"""Profile-local collection index, baseline merging and durable request quotas."""
from contextlib import closing
from hashlib import sha256
from itertools import chain, groupby
from operator import itemgetter
from pathlib import Path
from tmdbhelper.lib.collections.database import CollectionDatabase, DATABASE_VERSION
import sqlite3


class RuntimeCollectionDatabase(CollectionDatabase):
    def initialise(self):
        super().initialise()
        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS daily_requests (day TEXT PRIMARY KEY, attempts INTEGER NOT NULL)')
        self.connection.commit()

    def merge_baseline(self, filename):
        filename = Path(filename).resolve()
        digest = sha256(filename.read_bytes()).hexdigest()
        if self.get_metadata('baseline_sha256') == digest:
            return False
        self.connection.execute('ATTACH DATABASE ? AS baseline', (f'{filename.as_uri()}?mode=ro',))
        try:
            version = self.connection.execute('PRAGMA baseline.user_version').fetchone()[0]
            if version != DATABASE_VERSION:
                raise ValueError(f'Unsupported bundled collection database version: {version}')
            self.merge_attached_baseline(digest)
        finally:
            self.connection.execute('DETACH DATABASE baseline')
        return True

    def merge_attached_baseline(self, digest):
        snapshot = self.connection.execute(
            "SELECT value FROM baseline.metadata WHERE key='snapshot_date'").fetchone()[0]
        with self.connection:
            self.prepare_baseline_updates()
            self.merge_baseline_members()
            self.merge_baseline_attempts()
            self.merge_baseline_inventory(snapshot)
            self.set_metadata({'baseline_sha256': digest})
            self.connection.execute('DROP TABLE baseline_updates')

    def prepare_baseline_updates(self):
        self.connection.execute('DROP TABLE IF EXISTS temp.baseline_updates')
        self.connection.execute(
            '''
            CREATE TEMP TABLE baseline_updates AS
            SELECT source.collection_id, local.collection_id IS NULL AS is_new FROM baseline.collection AS source
            LEFT JOIN collection AS local USING (collection_id)
            WHERE local.collection_id IS NULL OR (
                source.last_checked_at IS NOT NULL AND (
                    local.last_checked_at IS NULL OR source.last_checked_at > local.last_checked_at))
            ''')
        self.connection.execute('INSERT OR IGNORE INTO collection SELECT * FROM baseline.collection')

    def merge_baseline_members(self):
        self.connection.execute(
            '''
            DELETE FROM collection_movie WHERE collection_id IN (SELECT collection_id FROM baseline_updates)
            ''')
        self.connection.execute(
            '''
            INSERT INTO collection_movie SELECT source.* FROM baseline.collection_movie AS source
            JOIN baseline_updates USING (collection_id)
            ''')
        self.connection.execute(
            '''
            UPDATE collection SET last_checked_at=(
                SELECT last_checked_at FROM baseline.collection AS source
                WHERE source.collection_id=collection.collection_id)
            WHERE collection_id IN (SELECT collection_id FROM baseline_updates)
            ''')

    def merge_baseline_attempts(self):
        self.connection.execute(
            '''
            UPDATE collection SET
                last_attempted_at=(SELECT last_attempted_at FROM baseline.collection AS b
                    WHERE b.collection_id=collection.collection_id),
                last_status=(SELECT last_status FROM baseline.collection AS b
                    WHERE b.collection_id=collection.collection_id),
                retry_after=(SELECT retry_after FROM baseline.collection AS b
                    WHERE b.collection_id=collection.collection_id),
                failure_count=(SELECT failure_count FROM baseline.collection AS b
                    WHERE b.collection_id=collection.collection_id)
            WHERE EXISTS (SELECT 1 FROM baseline.collection AS b
                WHERE b.collection_id=collection.collection_id
                AND COALESCE(b.last_attempted_at, '') > COALESCE(collection.last_attempted_at, ''))
            ''')

    def merge_baseline_inventory(self, snapshot):
        if snapshot < (self.get_metadata('snapshot_date') or ''):
            self.connection.execute(
                '''
                UPDATE collection SET active=0 WHERE collection_id IN (
                    SELECT collection_id FROM baseline_updates WHERE is_new=1)
                ''')
            return
        self.connection.execute(
            '''
            UPDATE collection SET active=COALESCE((
                SELECT active FROM baseline.collection AS b WHERE b.collection_id=collection.collection_id), 0)
            WHERE discovered_at<=?
            ''', (snapshot,))
        self.set_metadata({'snapshot_date': snapshot})

    def reserve_request(self, day, limit):
        with self.connection:
            self.connection.execute('INSERT OR IGNORE INTO daily_requests (day, attempts) VALUES (?, 0)', (day,))
            cursor = self.connection.execute(
                'UPDATE daily_requests SET attempts=attempts+1 WHERE day=? AND attempts<?', (day, limit))
            return cursor.rowcount == 1

    def get_requests_used(self, day):
        row = self.connection.execute('SELECT attempts FROM daily_requests WHERE day=?', (day,)).fetchone()
        return row[0] if row else 0

    def defer_retry(self, collection_id, retry_after):
        with self.connection:
            self.set_metadata({'api_retry_after': retry_after})
            self.connection.execute(
                "UPDATE collection SET retry_after=MAX(COALESCE(retry_after, ''), ?) WHERE collection_id=?",
                (retry_after, collection_id))

    def get_collection_movies(self, movie_ids):
        collections = self.get_related_collection_ids(movie_ids)
        batches = self.get_query_batches(collections)
        rows = chain.from_iterable(map(self.get_member_batch, batches))
        return {
            collection_id: self.map_members(members)
            for collection_id, members in groupby(rows, key=itemgetter(0))
        }

    def get_related_collection_ids(self, movie_ids):
        identifiers = tuple(dict.fromkeys(int(value) for value in movie_ids))
        batches = self.get_query_batches(identifiers)
        return sorted(set(chain.from_iterable(map(self.get_collection_id_batch, batches))))

    @staticmethod
    def get_query_batches(identifiers):
        return (identifiers[offset:offset + 500] for offset in range(0, len(identifiers), 500))

    def get_collection_id_batch(self, identifiers):
        placeholders = ','.join('?' for value in identifiers)
        rows = self.connection.execute(
            'SELECT DISTINCT collection_id FROM collection_movie JOIN collection USING (collection_id) '
            f'WHERE active=1 AND movie_id IN ({placeholders})', identifiers)
        return [row[0] for row in rows]

    def get_member_batch(self, identifiers):
        placeholders = ','.join('?' for value in identifiers)
        return self.connection.execute(
            'SELECT collection_id, movie_id, release_date FROM collection_movie '
            f'WHERE collection_id IN ({placeholders}) ORDER BY collection_id, release_date, movie_id', identifiers)

    @staticmethod
    def map_members(rows):
        return [{'movie_id': movie_id, 'release_date': release_date} for collection_id, movie_id, release_date in rows]


class CollectionIndex:
    def __init__(self, filename, baseline):
        self.filename = Path(filename)
        self.baseline = Path(baseline)

    def initialise(self):
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.filename, timeout=30, uri=True)) as connection:
            database = RuntimeCollectionDatabase(connection)
            database.initialise()
            database.merge_baseline(self.baseline)

    def get_collection_movies(self, movie_ids):
        self.initialise()
        with closing(sqlite3.connect(f'{self.filename.resolve().as_uri()}?mode=ro', uri=True)) as connection:
            connection.execute('BEGIN')
            return RuntimeCollectionDatabase(connection).get_collection_movies(movie_ids)
