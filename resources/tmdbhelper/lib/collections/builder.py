"""Resumable baseline construction and atomic publication outside Kodi."""
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from tmdbhelper.lib.collections.client import CollectionAPIError, RequestBudgetExceeded, get_utc_timestamp
from tmdbhelper.lib.collections.database import CollectionDatabase, DATABASE_PATH
import hashlib
import json
import os
import sqlite3
import time


CollectionFetchResult = namedtuple('CollectionFetchResult', 'collection_id movies attempted_at error')


class CollectionBuilder:
    def __init__(self, client, progress=print, workers=8):
        self.client = client
        self.progress = progress
        self.workers = workers

    @staticmethod
    def get_fingerprint(filename):
        try:
            source = filename.open('rb')
        except FileNotFoundError:
            return 'absent'
        digest = hashlib.sha256()
        with source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()

    def initialise_work(self, connection, filename):
        writer = CollectionDatabase(connection)
        exists = writer.get_version() != 0
        fingerprint = self.get_fingerprint(filename)
        if exists:
            writer.initialise()
            if writer.get_metadata('base_sha256') != fingerprint:
                raise ValueError(
                    'The published baseline changed after this checkpoint; '
                    'use another output path or remove the old checkpoint')
            return writer
        if filename.exists():
            with closing(sqlite3.connect(f'{filename.as_uri()}?mode=ro', uri=True)) as source:
                source.backup(connection)
        writer.initialise()
        with connection:
            writer.set_metadata({'base_sha256': fingerprint, 'run_started_at': get_utc_timestamp()})
        return writer

    def fetch_collection(self, collection_id):
        try:
            return CollectionFetchResult(
                collection_id, self.client.get_collection(collection_id), get_utc_timestamp(), None)
        except (CollectionAPIError, RequestBudgetExceeded) as error:
            return CollectionFetchResult(collection_id, None, get_utc_timestamp(), error)

    def process_queue(self, writer, queue):
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            return self.process_batches(writer, executor, queue)

    def process_batches(self, writer, executor, queue):
        completed = 0
        started = time.monotonic()
        for offset in range(0, len(queue), self.workers):
            batch = queue[offset:offset + self.workers]
            processed, exhausted = self.process_batch(writer, executor, batch)
            completed += processed
            self.report_progress(completed, len(queue), started)
            if exhausted:
                return True
        return False

    def process_batch(self, writer, executor, batch):
        completed = 0
        exhausted = False
        for result in executor.map(self.fetch_collection, batch):
            if isinstance(result.error, RequestBudgetExceeded):
                exhausted = True
                continue
            self.save_result(writer, result)
            completed += 1
        return completed, exhausted

    def save_result(self, writer, result):
        collection_id, movies, attempted_at, error = result
        if error is None:
            writer.set_collection(collection_id, movies, attempted_at)
            return
        writer.set_failure(collection_id, attempted_at, error.status)
        self.progress(str(error))
        if error.status in (401, 403):
            raise error

    def report_progress(self, completed, total, started):
        if completed and (completed % 200 < self.workers or completed == total):
            self.progress(
                f'Checked {completed}/{total} collections; '
                f'{self.client.detail_requests} requests; {time.monotonic() - started:.0f}s')

    def run(self, snapshot_date, filename=DATABASE_PATH, due_only=False):
        filename = Path(filename).resolve()
        filename.parent.mkdir(parents=True, exist_ok=True)
        work_path = filename.with_name(f'{filename.stem}.work.db')
        started = time.monotonic()
        identifiers, digest, export_size = self.client.get_export(snapshot_date)
        self.progress(f'Export {snapshot_date}: {len(identifiers)} collections, {export_size} compressed bytes')
        with closing(sqlite3.connect(work_path)) as connection:
            writer = self.initialise_work(connection, filename)
            self.configure_refresh(writer, due_only)
            writer.set_snapshot(identifiers, snapshot_date.isoformat(), digest)
            exhausted = self.populate(writer, due_only, work_path)
            counts = writer.get_counts()
            report = self.get_report(counts, exhausted, snapshot_date, started)
            if report['published']:
                self.finalise_checkpoint(writer, counts, filename)
        if not report['published']:
            self.progress(f'Checkpoint retained; published baseline unchanged: {json.dumps(report, sort_keys=True)}')
            return report
        work_path.unlink()
        self.progress(f'Published {filename.name}: {json.dumps(report, sort_keys=True)}')
        return report

    def populate(self, writer, due_only, work_path):
        queue = writer.get_queue(writer.get_metadata('run_started_at'), datetime.now(timezone.utc), due_only)
        self.progress(f'Queued {len(queue)} collections; checkpoint: {work_path.name}')
        return self.process_queue(writer, queue)

    def finalise_checkpoint(self, writer, counts, filename):
        self.set_build_metadata(writer, counts)
        writer.validate()
        self.publish(writer.connection, filename)

    @staticmethod
    def configure_refresh(writer, due_only):
        previous_mode = writer.get_metadata('run_due_only')
        if previous_mode is not None and previous_mode != str(due_only):
            raise ValueError('Resume the checkpoint with the same --due-only setting')
        with writer.connection:
            writer.set_metadata({'run_due_only': due_only})

    def get_report(self, counts, exhausted, snapshot_date, started):
        return dict(
            counts, published=not exhausted and not counts['unresolved'], budget_exhausted=exhausted,
            detail_requests=self.client.detail_requests, export_requests=self.client.export_requests,
            elapsed_seconds=round(time.monotonic() - started, 2), snapshot_date=snapshot_date.isoformat())

    @staticmethod
    def set_build_metadata(writer, counts):
        metadata = {
            'updated_at': get_utc_timestamp(), 'source': 'https://www.themoviedb.org',
            'created_at': writer.get_metadata('created_at') or writer.get_metadata('run_started_at'),
            **{f'count_{key}': value for key, value in counts.items()},
        }
        with writer.connection:
            writer.set_metadata(metadata)

    @staticmethod
    def publish(connection, filename):
        # Keep the resumable checkpoint intact until atomic publication succeeds.
        with NamedTemporaryFile(prefix='collections-', suffix='.db', dir=filename.parent, delete=False) as temporary:
            publish_path = Path(temporary.name)
        try:
            CollectionBuilder.write_publication(connection, publish_path)
            os.replace(publish_path, filename)
        finally:
            publish_path.unlink(missing_ok=True)

    @staticmethod
    def write_publication(connection, publish_path):
        with closing(sqlite3.connect(publish_path)) as destination:
            connection.backup(destination)
            database = CollectionDatabase(destination)
            with destination:
                database.delete_metadata(('base_sha256', 'run_started_at', 'run_due_only'))
            database.compact()
            database.validate()
