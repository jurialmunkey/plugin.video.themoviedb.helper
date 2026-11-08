"""Opt-in, per-batch service profiling without instrumenting shared item factories."""

from collections import Counter, defaultdict
from contextlib import contextmanager
from math import ceil
from secrets import token_hex
from threading import RLock, current_thread
from time import perf_counter
from traceback import format_exc
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.tmdate import get_datetime_now
from tmdbhelper.lib.files.futils import write_to_file
from tmdbhelper.lib.items.database.details.backend import DetailsBackend
from tmdbhelper.lib.items.database.details.protocol import DetailsServiceError, encode_message
from tmdbhelper.lib.items.database.details.profiling_details import (
    DetailsMemoryEstimate, DetailsWorkProfiler, ProfiledDetailsDatabase, ProfiledItemMetadataCache,
)
from tmdbhelper.lib.items.database.details.profiling_factories import ProfiledDetailsLookup
from tmdbhelper.lib.items.database.details.timing import (
    DetailsBatchTimings,
    TimedDetailsCoordinator,
    TimedDetailsRequestHandler,
)


class DetailsTimings:
    def __init__(self, lock):
        self.lock = lock
        self.timings = defaultdict(list)
        self.counts = Counter()

    def add_time(self, stage, seconds):
        with self.lock:
            self.timings[stage].append(seconds)

    def count(self, name, amount=1):
        with self.lock:
            self.counts[name] += amount

    def get_total(self, stage):
        with self.lock:
            return sum(self.timings.get(stage, ()))

    @contextmanager
    def measure(self, stage):
        started = perf_counter()
        try:
            yield
        finally:
            self.add_time(stage, perf_counter() - started)

    def call(self, stage, func, *args, **kwargs):
        with self.measure(stage):
            return func(*args, **kwargs)


class DetailsItemProfile(DetailsTimings):
    def __init__(self, report, request, dependency):
        super().__init__(report.lock)
        self.report = report
        self.request = request
        self.dependency = dependency
        self.number = len(report.records) + 1
        self.submitted = perf_counter()
        self.marks = {'submitted': self.submitted}
        self.resolution = 'pending'
        self.shared = ''
        self.outcome = 'pending'
        self.error = ''
        self.last_lookup = None
        self.future = None
        self.priority = 'standard'

    @property
    def reference(self):
        return f'{self.report.identifier}#{self.number}'

    def mark(self, name):
        with self.lock:
            self.marks[name] = perf_counter()

    def interval(self, stage, start, end):
        with self.lock:
            try:
                seconds = self.marks[end] - self.marks[start]
            except KeyError:
                return  # A timed-out/failed job may never reach the later phase.
            self.add_time(stage, seconds)

    def complete(self, future):
        with self.lock:
            self.marks.setdefault('finished', perf_counter())
            if future.cancelled():
                self.outcome = 'cancelled'
                return
            error = future.exception()
            self.error = str(error) if error else ''
            self.outcome = 'error' if error else ('details' if future.result() is not None else 'empty')

    def snapshot(self, now):
        with self.lock:
            # Future.result() may wake the handler before completion callbacks run.
            # Read the ready future too, so a completed item is never reported as pending.
            if self.future is not None and self.future.done() and self.outcome == 'pending':
                self.complete(self.future)
            return {
                'number': self.number, 'request': self.request.as_dict(),
                'identity': self.request.identity, 'dependency': self.dependency,
                'resolution': self.resolution, 'shared': self.shared,
                'priority': self.priority,
                'outcome': self.outcome, 'error': self.error,
                'elapsed': self.marks.get('finished', now) - self.submitted,
                'offset': self.submitted - self.report.started,
                'timings': {name: list(values) for name, values in self.timings.items()},
                'counts': self.counts.copy(),
            }


class DetailsBatchReport(DetailsTimings, DetailsBatchTimings):
    folder = 'timer_report/item_details'

    def __init__(self, entries, message, started):
        super().__init__(RLock())
        self.started = started
        self.timestamp = get_datetime_now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        self.identifier = f'{self.timestamp}_{token_hex(4)}'
        self.entries = len(entries)
        self.lookups = sum(entry['request'] is not None for entry in entries)
        self.merge_items = sum(entry['item'] is not None for entry in entries)
        self.kodi_details = bool(message.get('kodi_details'))
        self.records = []
        self.state = 'processing'
        self.error = ''
        self.response_bytes = 0
        self.scheduler = {}
        self.item_errors = {}
        self.details_python_bytes = 0
        self.metadata_cache = {}

    def add_request(self, request, dependency):
        with self.lock:
            record = DetailsItemProfile(self, request, dependency)
            self.records.append(record)
            return record

    def set_error(self, error):
        self.state = 'error'
        self.error = str(error)

    @staticmethod
    def timing_rows(timings):
        rows = ['stage | calls | total ms | mean ms | p95 ms | max ms']
        rows.extend(
            f'{name} | {len(values)} | {sum(values) * 1000:.3f} | '
            f'{sum(values) * 1000 / len(values):.3f} | '
            f'{sorted(values)[ceil(len(values) * 0.95) - 1] * 1000:.3f} | {max(values) * 1000:.3f}'
            for name, values in sorted(timings.items(), key=lambda item: sum(item[1]), reverse=True))
        return rows

    @staticmethod
    def item_rows(item):
        header = (
            f"#{item['number']} {'dependency' if item['dependency'] else 'requested'} {item['identity']} "
            f"priority={item['priority']} resolution={item['resolution']} outcome={item['outcome']} "
            f"elapsed_ms={item['elapsed'] * 1000:.3f} submitted_at_ms={item['offset'] * 1000:.3f}")
        rows = [header, f"  options={item['request']}", f"  counts={dict(item['counts'])}"]
        if item['shared']:
            rows.append(f"  shared_job={item['shared']}")
        if item['error']:
            rows.append(f"  error={item['error']}")
        rows.extend(f'  {row}' for row in DetailsBatchReport.timing_rows(item['timings']))
        return rows

    def get_report(self):
        now = perf_counter()
        with self.lock:
            items = [record.snapshot(now) for record in self.records]
            timings = {name: list(values) for name, values in self.timings.items()}
            counts = self.counts.copy()
            metadata_cache = self.metadata_cache.copy()
        work = defaultdict(list)
        work_counts = Counter()
        for item in items:
            work_counts.update(item['counts'])
            for stage, values in item['timings'].items():
                work[stage].extend(values)
        elapsed = now - self.started
        rows = [
            f'ITEM DETAILS BATCH {self.identifier}',
            f'status={self.state} error={self.error!r}',
            f'entries={self.entries} detail_requests={self.lookups} merge_items={self.merge_items} '
            f'kodi_only={self.entries - self.lookups} kodi_details={self.kodi_details}',
            f'wall_ms={elapsed * 1000:.3f} entries_per_second={self.entries / elapsed:.3f} '
            f'response_bytes={self.response_bytes}',
            f'details_python_bytes_estimate={self.details_python_bytes}',
            f'assembled_metadata_cache={metadata_cache}',
            'profiling=targeted_stage_timers function_capture=disabled',
            'scheduling=parallel_cache_reads_online_fast_track',
            f'dependencies={sum(item["dependency"] for item in items)} '
            f'outcomes={dict(Counter(item["outcome"] for item in items))} '
            f'resolutions={dict(Counter(item["resolution"] for item in items))}',
            f'batch_counts={dict(counts)}', f'item_work_counts={dict(work_counts)}',
            f'item_errors_by_entry_index={self.item_errors}',
            f'scheduler_at_admission={self.scheduler}',
            '', 'BATCH STAGES', *self.timing_rows(timings),
            '', 'ITEM WORK (requested items and dependencies)', *self.timing_rows(work),
            '', 'INTERPRETATION',
            'All durations use a high-resolution monotonic clock. Report writing is excluded from wall time.',
            'Batch details includes sync_wait, submit and result waiting; send_response includes encoding.',
            'Item stages are inclusive and can overlap; totals are work, not batch wall time.',
            'cache_read includes factory configuration, database queries, related metadata and output mapping.',
            'db_read includes item-details SELECT construction, execute, fetch and row materialisation; '
            'db_read.<table> groups by the first FROM table, including its joins/subqueries.',
            'sql_execute counts database-interface execute/executemany calls; parameter_sets counts their input rows. '
            'Direct transaction-control/setup statements and other databases are excluded from these counters.',
            'cache_read_other is cache_read minus its measured db_read time; '
            'it includes mapping, host calls, other work and instrumentation overhead.',
            'item_mapping includes related database reads. '
            'metadata_assembly measures reusable mapping, including artwork, on misses; '
            'label_mapping, extended_mapping, related_properties_mapping, cast_mapping, artwork_mapping '
            'and unique_ids_mapping break down metadata assembly.',
            'synced_state_read measures simplecache row retrieval. fresh_labels_mapping and '
            'fresh_properties_mapping apply current sync routes; fresh_state_mapping covers the remaining '
            'current-state calculations, including their date formatting. airdate_mapping covers the final '
            'premiered/duration formatting. These scopes differ from older function-derived helper totals.',
            'Stage timers are explicit factory/mapper/database scopes on each operation\'s thread. '
            'No interpreter function hooks are installed. Stage call counts are in item_work_counts. '
            'Do not add nested stage rows together. Instrumentation overhead differs from older '
            'cProfile/profile.Profile reports, so their absolute durations are not directly comparable.',
            'details_python_bytes_estimate counts unique Python objects in returned details '
            'before entry/Kodi merging; '
            'it excludes native memory, service caches and process RSS. profile_details_size times the estimate.',
            'assembled_metadata_cache is retained state after this batch\'s last cache read, '
            'not incremental process memory. protected counts entries found again since they were stored; '
            'entries seen once are evicted first. The byte estimate includes keys and conservatively counts '
            'values shared across entries again. metadata_hits/misses/invalidations/evictions are per-item counts; '
            'service saves discard only entries they can change (metadata_discard, metadata_discarded_entries) '
            'and metadata_save_scope_all saves invalidate every entry. Writes outside the service, such as ratings '
            'and synced play data, do not invalidate reuse; changes to item details outside it request invalidation. '
            'metadata_store includes sizing/eviction, and metadata_copy isolates returned containers.',
            'stored_read times reading and decoding a stored copy after a memory miss; '
            'stored_hits skip metadata_assembly, and stored_queued counts assembled copies queued for storage.',
            'fetch includes worker factory setup, provider/cache requests, source mapping and write-queue generation.',
            'commit includes the richer-cache recheck and transaction; '
            'write_operations counts queued callbacks, not SQL statements.',
            'admission_queue is submit to read start. admission is read start until the coordinator observes '
            'the result, including reader time and event waiting; cache_read is the read on its reader thread. '
            'read_completion is coordinator handling of the result; miss_lookup covers sharing or queuing a miss. '
            'dependency_wait ends when dependencies permit readiness.',
            'Single-item submissions use the fast_track lane for cache checks, online dispatch and commits. '
            'Parent dependencies inherit the lane; shared jobs are promoted without another fetch. '
            'priority_promotions counts promoted jobs and fetches_<lane> counts actual worker dispatches.',
            'Cached reads run on read_workers reader threads, each with its own connection; a read starts '
            'when a reader is free. Commits run only while no reads are in flight; while commits wait, '
            'reads pause after admission_cap reads since the last commit. '
            'One online worker slot is reserved for fast_track work. Standard admissions retain batch order; '
            'online misses rotate between batches. After two priority admissions/dispatches, '
            'eligible standard work gets a turn. Starting reads yields to new events.',
            'worker_queue is readiness to fetch start, including dispatch cache rechecks and worker availability.',
            'commit_queue is fetch completion to commit processing, including completion_event_queue.',
            'Shared jobs are charged to their original batch/item; shared_job links the waiting item to that work.',
            'Elapsed item times include waiting. Pending items are snapshots at response time and may finish later.',
            'Receive/validate starts at handler entry; '
            'client startup, connect and client-side processing are excluded.',
            '', 'ITEMS (slowest elapsed first)',
        ]
        for item in sorted(items, key=lambda item: item['elapsed'], reverse=True):
            rows.extend(self.item_rows(item))
        return '\n'.join(rows) + '\n'

    def write(self):
        write_to_file(self.get_report(), self.folder, f'{self.identifier}.txt', join_addon_data=True)


class DetailsProfileRegistry:
    """Keep each request's profile alive until its future is complete, including after timeout."""

    def __init__(self):
        self.lock = RLock()
        self.records = {}

    def add(self, request, report, dependency):
        record = report.add_request(request, dependency)
        with self.lock:
            self.records[id(request)] = record
        return record

    def get(self, request):
        with self.lock:
            return self.records.get(id(request))

    def complete(self, request, record, future):
        record.complete(future)
        with self.lock:
            del self.records[id(request)]


class ProfiledDetailsBackend(DetailsBackend):
    lookup_class = ProfiledDetailsLookup

    def __init__(self, profiles):
        super().__init__()
        self.profiles = profiles
        self.work_profiler = DetailsWorkProfiler()

    @cached_property
    def cache(self):
        return ProfiledDetailsDatabase(self.work_profiler)

    def get_metadata_cache(self):
        return ProfiledItemMetadataCache(self.cache, self.stored_metadata, self.work_profiler)

    def call(self, request, stage, func, *args):
        record = self.profiles.get(request)
        if record is None:
            return func(request, *args)
        return self.work_profiler.call(record, record.call, stage, func, request, *args)

    def lookup(self, request, parent_data=None, connection=None):
        lookup = self.call(request, 'factory_configuration', super().lookup, parent_data, connection)
        record = self.profiles.get(request)
        if record is not None:
            record.last_lookup = lookup
        return lookup

    def read(self, request, connection=None):
        record = self.profiles.get(request)
        before = record.get_total('db_read') if record is not None else 0
        data = self.call(request, 'cache_read', super().read, connection)
        if record is not None:
            database_time = record.get_total('db_read') - before
            record.add_time('cache_read_other', max(record.timings['cache_read'][-1] - database_time, 0))
            record.count('cache_hits' if data is not None else 'cache_misses')
            with record.report.lock:
                record.report.metadata_cache = {
                    'entries': len(self.metadata_cache.entries),
                    'protected': len(self.metadata_cache.entries.protected),
                    'python_bytes_estimate': self.metadata_cache.size,
                    'entry_limit': self.metadata_cache.max_entries,
                    'byte_limit': self.metadata_cache.max_bytes,
                }
            record.last_lookup = None
        return data

    def fetch(self, request, parent_data):
        record = self.profiles.get(request)
        if record is None:
            return super().fetch(request, parent_data)
        with record.lock:
            record.resolution = 'fetch'
        record.mark('fetch_started')
        record.interval('worker_queue', 'ready', 'fetch_started')
        try:
            queue = self.call(request, 'fetch', super().fetch, parent_data)
            record.count('write_operations', len(queue))
            return queue
        finally:
            record.mark('fetch_finished')

    def commit(self, request, queue):
        return self.call(request, 'commit', super().commit, queue)

    def fallback(self, request):
        data = self.call(request, 'fallback', super().fallback)
        record = self.profiles.get(request)
        if record is not None:
            record.count('fallback_details' if data is not None else 'fallback_empty')
            record.last_lookup = None
        return data


class ProfiledDetailsCoordinator(TimedDetailsCoordinator):
    def __init__(self):
        self.profiles = DetailsProfileRegistry()
        super().__init__(backend_class=lambda: ProfiledDetailsBackend(self.profiles))

    def submit(self, requests, group=None, fast_track=None):
        if not isinstance(group, DetailsBatchReport):
            return super().submit(requests, group, fast_track)
        # Each occurrence needs its own profile even if a caller repeats the same
        # immutable request object. Values and the coordinator's dedup keys are unchanged.
        requests = [request.__class__(**request.as_dict()) for request in requests]
        records = [self.profiles.add(request, group, current_thread() is self) for request in requests]
        fast_track = len(requests) == 1 if fast_track is None else fast_track
        for record in records:
            record.priority = 'fast_track' if fast_track else 'standard'
        futures = super().submit(requests, group, fast_track)
        for request, record, future in zip(requests, records, futures):
            record.future = future
            future.add_done_callback(
                lambda future, request=request, record=record: self.profiles.complete(request, record, future))
        return futures

    def process_event(self, kind, *args):
        if kind == 'submit':
            items, group = args
            if isinstance(group, DetailsBatchReport) and not group.scheduler:
                with group.lock:
                    group.scheduler = self.scheduler_snapshot
        return super().process_event(kind, *args)

    @property
    def scheduler_snapshot(self):
        return {
            'active_reads': self.reading,
            'read_workers': self.read_workers,
            'reads_since_commit': self.reads_since_commit,
            'active_workers': self.active,
            'active_standard_workers': self.active_regular,
            'worker_limit': self.batch_size,
            'reserved_fast_track_workers': self.reserved_workers,
            'pending_jobs': len(self.pending),
            'ready_jobs': len(self.ready),
            'completed_jobs': len(self.completed),
            'admission_groups': self.admissions.group_count,
            'admission_items': len(self.admissions),
            'fast_track_admission_items': len(self.fast_track.admissions),
            'fast_track_ready_jobs': len(self.fast_track.ready),
            'fast_track_completed_jobs': len(self.fast_track.completed),
            'commit_backlogged': self.is_commit_backlogged,
        }

    def start_read(self, admission):
        record = self.profiles.get(admission.request)
        if record is not None:
            record.priority = 'fast_track' if admission.fast_track else 'standard'
            record.count(f'admissions_{record.priority}')
            record.mark('admitted')
            record.interval('admission_queue', 'submitted', 'admitted')
        return super().start_read(admission)

    def read_completed(self, admission, future):
        record = self.profiles.get(admission.request)
        if record is None:
            return super().read_completed(admission, future)
        record.mark('read_observed')
        record.interval('admission', 'admitted', 'read_observed')
        try:
            record.call('read_completion', super().read_completed, admission, future)
            self.set_resolution(record, admission.request, admission.future)
        finally:
            with record.lock:
                record.marks.setdefault('admission_finished', perf_counter())
            record.last_lookup = None

    def lookup(self, request, future, group, fast_track=False):
        record = self.profiles.get(request)
        if record is None:
            return super().lookup(request, future, group, fast_track)
        try:
            record.call('miss_lookup', super().lookup, request, future, group, fast_track)
            self.set_resolution(record, request, future)
        finally:
            record.mark('admission_finished')
            record.last_lookup = None

    def set_resolution(self, record, request, future):
        with record.lock:
            if future.done():
                if request.cache_refresh == 'never':
                    record.resolution = 'cache_only'
                else:
                    record.resolution = 'cache' if record.counts['cache_hits'] else 'no_fetch'
            elif record.last_lookup is not None:
                job = self.pending[record.last_lookup.key]
                if job.request is not request:
                    record.resolution = 'shared'
                    owner = self.profiles.get(job.request)
                    record.shared = owner.reference if owner is not None else 'unprofiled job'
                else:
                    record.resolution = 'lookup'
                    record.count('dependencies', len(job.dependencies))

    def promote(self, job):
        record = self.profiles.get(job.request)
        if record is not None and not job.fast_track:
            with record.lock:
                record.priority = 'fast_track'
                record.count('priority_promotions')
                record.mark('promoted')
        return super().promote(job)

    def start_fetch(self, job):
        record = self.profiles.get(job.request)
        if record is not None:
            record.count('fetches_fast_track' if job.fast_track else 'fetches_standard')
        return super().start_fetch(job)

    def make_ready(self, job):
        record = self.profiles.get(job.request)
        if record is None:
            return super().make_ready(job)
        record.mark('ready')
        with record.lock:
            record.resolution = 'lookup'
        if job.dependencies:
            record.interval('dependency_wait', 'admission_finished', 'ready')
        try:
            return record.call('ready_check', super().make_ready, job)
        finally:
            record.last_lookup = None

    def finish(self, job):
        record = self.profiles.get(job.request)
        if record is not None and 'fetch_started' not in record.marks:
            with record.lock:
                record.resolution = 'cache_after_wait' if record.counts['cache_hits'] else 'no_fetch'
        return super().finish(job)

    def fetch_completed(self, job, future):
        record = self.profiles.get(job.request)
        if record is not None:
            record.mark('fetch_observed')
            record.interval('completion_event_queue', 'fetch_finished', 'fetch_observed')
        return super().fetch_completed(job, future)

    def commit_completed(self, job, future):
        record = self.profiles.get(job.request)
        if record is None:
            return super().commit_completed(job, future)
        record.mark('commit_started')
        record.interval('commit_queue', 'fetch_finished', 'commit_started')
        return record.call('commit_and_finish', super().commit_completed, job, future)


class ProfiledDetailsRequestHandler(TimedDetailsRequestHandler):
    def handle(self):
        self.report = None
        self.started = perf_counter()
        try:
            return super().handle()
        finally:
            if self.report is not None:
                try:
                    self.report.write()
                except Exception:
                    kodi_log(f'Item detail timer report failed:\n{format_exc()}', 1)

    def get_batch_response(self, entries, message):
        self.report = DetailsBatchReport(entries, message, self.started)
        self.report.add_time('receive_validate', perf_counter() - self.started)
        try:
            response = self.report.call('batch_response', super().get_batch_response, entries, message)
        except Exception as exc:
            self.report.set_error(exc)
            raise
        self.report.count('item_errors', len(response['errors']))
        self.report.item_errors = response['errors']
        self.report.count('returned_items', sum(item is not None for item in response['items']))
        self.report.count('empty_items', sum(item is None for item in response['items']))
        self.report.state = 'partial' if response['errors'] else 'ok'
        return response

    def get_batch_timings(self):
        """The batch report is the coordinator group, so it also holds the stage timings."""
        return self.report

    def get_detail_results(self, entries):
        results = self.report.call('details', super().get_detail_results, entries)
        with self.report.measure('profile_details_size'):
            self.report.details_python_bytes = DetailsMemoryEstimate.get_size([item for item, error in results])
        return results

    def wait_for_sync(self, requests, deadline):
        return self.report.call('sync_wait', super().wait_for_sync, requests, deadline)

    def submit_requests(self, requests):
        return self.report.call('submit', super().submit_requests, requests)

    def get_result(self, future, deadline):
        return self.report.call('result_wait', super().get_result, future, deadline)

    def get_entry_result(self, entry, result):
        return self.report.call('merge_entry', super().get_entry_result, entry, result)

    def get_kodi_results(self, entries, results):
        return self.report.call('kodi_enrichment', super().get_kodi_results, entries, results)

    def get_encoded_response(self, response):
        if self.report is None:
            return super().get_encoded_response(response)
        try:
            encoded = self.report.call('encoding', encode_message, response)
        except DetailsServiceError as exc:
            self.report.set_error(exc)
            encoded = self.report.call('encoding', encode_message, {'error': str(exc)})
        self.report.response_bytes = len(encoded)
        return encoded

    def send_response(self, response):
        if self.report is None:
            return super().send_response(response)
        try:
            return self.report.call('send_response', super().send_response, response)
        except OSError as exc:
            self.report.set_error(f'Response delivery failed: {exc}')
            raise
