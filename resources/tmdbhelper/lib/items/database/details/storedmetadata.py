"""Keep assembled item metadata in the item details database between service runs."""

import json
from hashlib import sha1
from threading import Lock
from time import time
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.details.metadata import DetailsSavedItemScope


class DetailsStoredMetadataCopy:
    """A memory cache entry prepared for storage. Keys follow ItemMetadataCache.get_key():
    the mapper class, the item id, then the values the assembled item was built from."""

    def __init__(self, key, item=None):
        self.key = key
        self.item = item

    @cached_property
    def mapper_class(self):
        return self.key[0]

    @cached_property
    def item_id(self):
        return self.key[1]

    @cached_property
    def family_id(self):
        return DetailsSavedItemScope(self.item_id, ()).family_id

    @cached_property
    def reads_other_items(self):
        return int(self.mapper_class.reads_other_items)

    @cached_property
    def hash(self):
        return self.get_hash()

    def get_hash(self):
        mapper_name = f'{self.mapper_class.__module__}.{self.mapper_class.__qualname__}'
        return sha1(repr((mapper_name, *self.key[1:])).encode('utf-8')).hexdigest()

    @cached_property
    def text(self):
        return json.dumps(self.item, separators=(',', ':'), ensure_ascii=False)


class DetailsStoredMetadata:
    """Stored copies of assembled item metadata, so a cold start can skip assembling items.

    Reader threads read stored copies on their own connections and queue new copies. Only
    the coordinator writes, while no reads are in flight. Saves delete the stored copies
    they can change in the same transaction as the item, and every memory cache clear
    also clears the stored copies, so a stored copy is never older than its item.
    """

    format_version = 1  # Raise when the shape of get_stable_item() output changes
    unused_days = 14  # Maintenance prunes copies that have not been used for this long

    def __init__(self, database):
        self.database = database
        self.lock = Lock()
        self.pending = {}
        self.touched = set()
        self.wiping = False

    @property
    def today(self):
        return int(time() // 86400)

    @cached_property
    def fingerprint(self):
        return self.get_fingerprint()

    def get_fingerprint(self):
        """Only the settings read while assembling items change what stored copies contain."""
        from tmdbhelper.lib.addon.plugin import get_version
        from tmdbhelper.lib.items.database.details.settings import DetailsSettings
        state = {
            'version': get_version(),
            'format_version': self.format_version,
            'settings': DetailsSettings().get_stored_metadata_snapshot(),
        }
        return sha1(json.dumps(state, sort_keys=True).encode('utf-8')).hexdigest()

    @property
    def has_work(self):
        return bool(self.pending or self.touched or self.wiping)

    def prepare(self, cursor):
        """Clear copies built by another add-on version or with other settings."""
        row = cursor.execute("SELECT data FROM stored_metadata_state WHERE id='fingerprint'").fetchone()
        if row is not None and row[0] == self.fingerprint:
            return
        cursor.execute('BEGIN')
        try:
            cursor.execute('DELETE FROM stored_metadata')
            cursor.execute(
                "INSERT OR REPLACE INTO stored_metadata_state(id, data) VALUES ('fingerprint', ?)",
                (self.fingerprint, ))
            cursor.execute('COMMIT')
        except BaseException:
            cursor.execute('ROLLBACK')
            raise

    def read(self, key, cursor):
        """Return a stored copy, or None. Copies are not read while a clear is waiting."""
        if self.wiping:
            return
        stored = DetailsStoredMetadataCopy(key)
        row = cursor.execute('SELECT data, used FROM stored_metadata WHERE id=?', (stored.hash, )).fetchone()
        if row is None:
            return
        if row[1] != self.today:
            self.touch(stored.hash)
        return json.loads(row[0])

    def touch(self, stored_hash):
        with self.lock:
            self.touched.add(stored_hash)

    def queue(self, stored):
        """Queue a DetailsStoredMetadataCopy whose hash and text were prepared beforehand."""
        with self.lock:
            self.pending[stored.hash] = stored

    def discard_saved(self, factory):
        """Drop queued copies that a save of this factory's item can change."""
        with self.lock:
            if factory.metadata_save_scope != 'family':
                self.pending.clear()
                return
            scope = DetailsSavedItemScope(factory.item_id, ())
            self.pending = {
                stored_hash: stored
                for stored_hash, stored in self.pending.items()
                if not stored.reads_other_items and not scope.is_family(stored.item_id)
            }

    def discard_all(self):
        """Stop reading copies and drop queued ones until the next flush clears the table."""
        with self.lock:
            self.pending.clear()
            self.touched.clear()
            self.wiping = True

    def delete_saved(self, factory, cursor):
        """Delete stored copies that a save can change, inside the save's transaction."""
        if factory.metadata_save_scope != 'family':
            cursor.execute('DELETE FROM stored_metadata')
            return
        cursor.execute(
            'DELETE FROM stored_metadata WHERE family_id=? OR reads_other_items=1',
            (DetailsSavedItemScope(factory.item_id, ()).family_id, ))

    def get_pending_rows(self, pending):
        today = self.today
        return [
            (
                stored.hash, stored.item_id, stored.family_id, stored.reads_other_items,
                stored.text, today, stored.item_id,
            )
            for stored in pending
        ]

    def flush(self, cursor):
        """Write queued copies and use dates. Copies of deleted items are skipped."""
        with self.lock:
            wiping = self.wiping
            pending, self.pending = tuple(self.pending.values()), {}
            touched, self.touched = tuple(self.touched), set()
        cursor.execute('BEGIN')
        try:
            if wiping:
                cursor.execute('DELETE FROM stored_metadata')
            cursor.executemany(
                'INSERT OR REPLACE INTO stored_metadata'
                '(id, item_id, family_id, reads_other_items, data, used) '
                'SELECT ?, ?, ?, ?, ?, ? WHERE EXISTS (SELECT 1 FROM baseitem WHERE id=?)',
                self.get_pending_rows(pending))
            cursor.executemany(
                'UPDATE stored_metadata SET used=? WHERE id=?',
                [(self.today, stored_hash) for stored_hash in touched])
            cursor.execute('COMMIT')
        except BaseException:
            cursor.execute('ROLLBACK')
            raise
        if not wiping:
            return
        # Clears and flushes both run on the coordinator thread, so none arrived meanwhile.
        with self.lock:
            self.wiping = False

    def clear(self):
        """Delete every stored copy, for changes made while the service is not running."""
        self.database.execute_sql('DELETE FROM stored_metadata')

    def prune(self):
        self.database.execute_sql(
            'DELETE FROM stored_metadata WHERE used<?', (self.today - self.unused_days, ))
