"""Storage shared by the standalone awards builder and Kodi reader."""
from contextlib import closing
from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).resolve().parents[3] / 'databases' / 'awards.db'
DATABASE_VERSION = 2
ITEM_SCHEMA = '''
    CREATE TABLE item (
        tmdb_type TEXT NOT NULL CHECK (tmdb_type IN ('movie', 'tv')),
        tvdb_id INTEGER NOT NULL,
        tmdb_id INTEGER,
        name TEXT NOT NULL,
        year TEXT,
        match_method TEXT NOT NULL DEFAULT '',
        match_reason TEXT NOT NULL DEFAULT '',
        PRIMARY KEY (tmdb_type, tvdb_id)
    );
    CREATE INDEX item_tmdb ON item (tmdb_type, tmdb_id);
'''
AWARDS_SCHEMA = '''
    CREATE TABLE category (
        tvdb_id INTEGER PRIMARY KEY,
        award_id INTEGER NOT NULL,
        award TEXT NOT NULL,
        name TEXT NOT NULL,
        position INTEGER NOT NULL
    );
    CREATE TABLE nomination (
        category_id INTEGER NOT NULL REFERENCES category (tvdb_id) ON DELETE CASCADE,
        nomination_id INTEGER NOT NULL,
        tmdb_type TEXT NOT NULL,
        tvdb_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        year TEXT,
        is_winner INTEGER NOT NULL CHECK (is_winner IN (0, 1)),
        PRIMARY KEY (category_id, nomination_id),
        FOREIGN KEY (tmdb_type, tvdb_id) REFERENCES item (tmdb_type, tvdb_id)
    );
    CREATE INDEX nomination_item ON nomination (tmdb_type, tvdb_id);
'''
DATABASE_SCHEMA = ITEM_SCHEMA + AWARDS_SCHEMA + 'CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);'


class AwardsDatabase:
    """Read a single item's nominations without retaining a database connection."""

    def __init__(self, filename=DATABASE_PATH):
        self.filename = Path(filename)

    def get_item_awards(self, tmdb_type, tmdb_id):
        uri = f'{self.filename.resolve().as_uri()}?mode=ro'
        with closing(sqlite3.connect(uri, uri=True)) as connection:
            rows = connection.execute(
                '''SELECT category.award, category.name, nomination.year, nomination.is_winner
                   FROM nomination JOIN category ON category.tvdb_id=nomination.category_id
                   WHERE nomination.tmdb_type=? AND nomination.tvdb_id IN (
                       SELECT tvdb_id FROM item WHERE tmdb_type=? AND tmdb_id=?)
                   ORDER BY category.position, nomination.position''',
                (tmdb_type, tmdb_type, tmdb_id)).fetchall()
        return self.get_grouped_awards(rows)

    @staticmethod
    def get_grouped_awards(rows):
        awards = {}
        for award, category, year, is_winner in rows:
            key = 'awards_won' if is_winner else 'awards_nominated'
            categories = awards.setdefault(key, {}).setdefault(award, [])
            categories.append(f'{category} ({year})')
        return awards


class AwardsDatabaseWriter:
    """Own schema changes and writes to the builder's unpublished database."""

    def __init__(self, connection):
        self.connection = connection
        self.connection.execute('PRAGMA foreign_keys=ON')

    def create(self):
        self.connection.executescript(DATABASE_SCHEMA)
        self.set_version()

    def upgrade(self):
        version = self.connection.execute('PRAGMA user_version').fetchone()[0]
        if version == DATABASE_VERSION:
            return
        if version != 1:
            raise ValueError(f'Unsupported awards database version: {version}')
        # Version 1 had no source nomination/category IDs. Refresh those tables
        # once from TVDB, retaining the item table and all established matches.
        self.connection.executescript('''
            ALTER TABLE item ADD COLUMN match_method TEXT NOT NULL DEFAULT '';
            ALTER TABLE item ADD COLUMN match_reason TEXT NOT NULL DEFAULT '';
            UPDATE item SET match_method='existing' WHERE tmdb_id IS NOT NULL;
            DROP TABLE nomination;
        ''' + AWARDS_SCHEMA)
        self.set_version()

    def set_version(self):
        self.connection.execute(f'PRAGMA user_version={DATABASE_VERSION}')

    def prepare_refresh(self):
        self.connection.executescript('''
            CREATE TEMP TABLE seen_category (tvdb_id INTEGER PRIMARY KEY);
            CREATE TEMP TABLE seen_nomination (
                category_id INTEGER NOT NULL,
                nomination_id INTEGER NOT NULL,
                PRIMARY KEY (category_id, nomination_id)
            );
        ''')

    def set_category(self, record, position):
        self.connection.execute(
            '''INSERT INTO category (tvdb_id, award_id, award, name, position) VALUES (?, ?, ?, ?, ?)
               ON CONFLICT (tvdb_id) DO UPDATE SET
                   award_id=excluded.award_id, award=excluded.award, name=excluded.name, position=excluded.position
               WHERE category.award_id IS NOT excluded.award_id OR category.award IS NOT excluded.award
                   OR category.name IS NOT excluded.name OR category.position IS NOT excluded.position''',
            (record['id'], record['award']['id'], record['award']['name'], record['name'], position))
        self.connection.execute('INSERT INTO seen_category (tvdb_id) VALUES (?)', (record['id'],))

    def set_item(self, tmdb_type, record):
        self.connection.execute(
            '''INSERT INTO item (tmdb_type, tvdb_id, name, year) VALUES (?, ?, ?, ?)
               ON CONFLICT (tmdb_type, tvdb_id) DO UPDATE SET name=excluded.name, year=excluded.year
               WHERE item.name IS NOT excluded.name OR item.year IS NOT excluded.year''',
            (tmdb_type, record['id'], record['name'], record.get('year')))

    def set_nomination(self, category_id, position, tmdb_type, tvdb_id, record):
        self.connection.execute(
            '''INSERT INTO nomination (
                   category_id, nomination_id, tmdb_type, tvdb_id, position, year, is_winner)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT (category_id, nomination_id) DO UPDATE SET
                   tmdb_type=excluded.tmdb_type, tvdb_id=excluded.tvdb_id,
                   position=excluded.position, year=excluded.year, is_winner=excluded.is_winner
               WHERE nomination.tmdb_type IS NOT excluded.tmdb_type OR nomination.tvdb_id IS NOT excluded.tvdb_id
                   OR nomination.position IS NOT excluded.position OR nomination.year IS NOT excluded.year
                   OR nomination.is_winner IS NOT excluded.is_winner''',
            (
                category_id, record['id'], tmdb_type, tvdb_id, position,
                record.get('year'), bool(record.get('isWinner'))))
        self.connection.execute(
            'INSERT INTO seen_nomination (category_id, nomination_id) VALUES (?, ?)',
            (category_id, record['id']))

    def remove_missing_nominations(self, category_id):
        self.connection.execute(
            '''DELETE FROM nomination WHERE category_id=? AND NOT EXISTS (
                   SELECT 1 FROM seen_nomination WHERE seen_nomination.category_id=nomination.category_id
                       AND seen_nomination.nomination_id=nomination.nomination_id)''',
            (category_id,))

    def remove_missing_categories(self):
        self.connection.execute('''
            DELETE FROM category WHERE NOT EXISTS (
                SELECT 1 FROM seen_category WHERE seen_category.tvdb_id=category.tvdb_id)
        ''')
        self.connection.execute('''
            DELETE FROM item WHERE NOT EXISTS (
                SELECT 1 FROM nomination WHERE nomination.tmdb_type=item.tmdb_type AND nomination.tvdb_id=item.tvdb_id)
        ''')

    def get_unmatched_items(self):
        return self.connection.execute('''
            SELECT tmdb_type, tvdb_id, name, year FROM item WHERE tmdb_id IS NULL ORDER BY tmdb_type, tvdb_id
        ''').fetchall()

    def set_match(self, tmdb_type, tvdb_id, match):
        self.connection.execute(
            'UPDATE item SET tmdb_id=?, match_method=?, match_reason=? WHERE tmdb_type=? AND tvdb_id=?',
            (match.tmdb_id, match.method, match.reason, tmdb_type, tvdb_id))

    def set_metadata(self, updated_at):
        matched = self.connection.execute('SELECT COUNT(*) FROM item WHERE tmdb_id IS NOT NULL').fetchone()[0]
        unmatched = self.connection.execute('SELECT COUNT(*) FROM item WHERE tmdb_id IS NULL').fetchone()[0]
        nominations = self.connection.execute('SELECT COUNT(*) FROM nomination').fetchone()[0]
        if not matched or not nominations:
            raise ValueError('Update has no matched items or nominations; refusing to publish')
        self.connection.execute(
            "INSERT INTO metadata (key, value) VALUES ('built_at', ?) ON CONFLICT (key) DO NOTHING", (updated_at,))
        self.connection.executemany(
            'INSERT INTO metadata (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value=excluded.value',
            (
                ('updated_at', updated_at), ('source', 'https://thetvdb.com'),
                ('matched_items', str(matched)), ('unmatched_items', str(unmatched)),
                ('nominations', str(nominations))))
        return matched, unmatched, nominations

    def validate(self):
        if self.connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise ValueError('Awards database failed integrity check')
        if self.connection.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Awards database failed foreign key check')
