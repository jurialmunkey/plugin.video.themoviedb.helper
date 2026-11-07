from collections import deque
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from threading import Event, RLock, Thread
from traceback import format_exc
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.items.database.details.backend import DetailsBackend
from tmdbhelper.lib.items.database.details.protocol import DetailsLookupError, DetailsServiceUnavailable
from tmdbhelper.lib.items.database.details.queues import (
    DetailsAdmission,
    DetailsAdmissionQueue,
    DetailsCommitQueue,
    DetailsFastTrackQueue,
    DetailsFuture,
    DetailsOnlineQueue,
)


class LookupJob:
    def __init__(self, request, key, waiter, group, fast_track=False):
        self.request = request
        self.key = key
        self.waiters = [waiter]
        self.dependencies = []
        self.parent_data = None
        self.ready = False
        self.group = group
        self.fast_track = fast_track
        self.queue = None
        self.fetch_future = None
        self.worker_fast_track = False


class DetailsCoordinator(Thread):
    """One scheduling/commit owner with separate cached, online and fast-track lanes.

    Cached reads run on reader threads with their own connections. Commits run only
    while no reads are in flight, so reads never overlap the service's own writes.
    """

    batch_size = 20
    reserved_workers = 1
    read_workers = 4
    admission_cap = 12  # Reads started between commit rounds while commits wait
    priority_cap = 2
    commit_cap = 2

    def __init__(self, backend_class=DetailsBackend):
        super().__init__(name='TMDbHelper item details')
        self.backend_class = backend_class
        self.events = Queue()
        self.events_waiting = Event()
        self.pending = {}
        self.admissions = DetailsAdmissionQueue()
        self.ready = DetailsOnlineQueue()
        self.completed = DetailsCommitQueue()
        self.fast_track = DetailsFastTrackQueue()
        self.active = 0
        self.active_regular = 0
        self.reading = 0
        self.reads_since_commit = 0
        self.priority_admissions = 0
        self.priority_dispatches = 0
        self.failure = None
        self.lock = RLock()
        self.waiters = set()
        self.stopping = False

    def submit(self, requests, group=None, fast_track=None):
        if not requests:
            return []
        fast_track = len(requests) == 1 if fast_track is None else fast_track
        futures = [DetailsFuture(fast_track) for request in requests]
        with self.lock:
            if self.stopping:
                for future in futures:
                    future.set_exception(DetailsServiceUnavailable('Item detail service is restarting'))
                return futures
            for future in futures:
                self.waiters.add(future)
                future.add_done_callback(self.remove_waiter)
            self.post_event('submit', deque(zip(requests, futures)), group or object())
        return futures

    def post_event(self, kind, *args):
        self.events.put((kind, *args))
        self.events_waiting.set()

    def invalidate(self):
        """Clear assembled metadata on the coordinator thread, which owns the backend."""
        self.post_event('invalidate')

    def remove_waiter(self, future):
        with self.lock:
            self.waiters.discard(future)
            future.clear_lookup()

    @property
    def has_work(self):
        return bool(
            self.can_admit
            or (self.has_commits and self.can_commit)
            or self.can_dispatch
        )

    @property
    def has_commits(self):
        return bool(self.completed or self.fast_track.completed)

    @property
    def can_commit(self):
        return not self.reading

    @property
    def is_read_paused(self):
        """Let waiting commits run once admission_cap reads have started since the last commit."""
        return self.has_commits and self.reads_since_commit >= self.admission_cap

    @property
    def can_read(self):
        return self.reading < self.read_workers and not self.is_read_paused

    @property
    def can_admit(self):
        return self.can_read and bool(self.admissions or self.fast_track.admissions)

    def get_batch(self):
        # Clear before draining so that a request submitted meanwhile is not missed.
        # Drain every queued event so that no request is left behind a cleared flag.
        self.events_waiting.clear()
        batch = [] if self.has_work else [self.events.get()]
        while True:
            try:
                batch.append(self.events.get_nowait())
            except Empty:
                return batch

    def run(self):
        self.backend = None
        self.executor = None
        self.reader = None
        try:
            self.backend = self.backend_class()
            self.executor = ThreadPoolExecutor(
                max_workers=self.batch_size,
                thread_name_prefix='TMDbHelper lookup',
            )
            self.reader = ThreadPoolExecutor(
                max_workers=self.read_workers,
                thread_name_prefix='TMDbHelper read',
            )
            while not self.stopping:
                batch = self.get_batch()
                if self.stopping:
                    break
                with self.backend.connection.open():
                    self.process_batch(batch)
        except BaseException as exc:
            self.failure = exc
            kodi_log(f'Item detail lookup failed:\n{format_exc()}', 1)
        finally:
            self.fail_waiters()
            if self.executor is not None:
                # A hung online lookup must not delay the restart. Late results
                # are discarded because nothing reads the event queue any more.
                self.executor.shutdown(wait=False)
            if self.reader is not None:
                # Local reads are short; finish them before their connections close.
                self.reader.shutdown(wait=True)
            if self.backend is not None:
                self.backend.close()

    def process_batch(self, batch):
        """Reuse the owner connection until all immediately runnable work and reads yield."""
        self.process_events(batch)
        self.run_turn()
        while not self.stopping and (self.has_work or self.reading or not self.events.empty()):
            self.process_events(self.get_batch())
            self.run_turn()

    def process_events(self, batch):
        for event in batch:
            self.process_event(*event)

    def run_turn(self):
        self.commit_queue(self.fast_track.completed)
        self.admit()
        self.dispatch()
        self.commit_pending()

    @property
    def can_continue(self):
        return not self.stopping and not self.events_waiting.is_set()

    def process_event(self, kind, *args):
        if kind == 'submit':
            self.process_submit(*args)
        elif kind == 'dependency':
            self.dependency_finished(*args)
        elif kind == 'fetched':
            self.fetch_completed(*args)
        elif kind == 'read':
            self.read_completed(*args)
        elif kind == 'invalidate':
            self.backend.metadata_cache.invalidate()

    def process_submit(self, items, group):
        for request, future in items:
            if future.done():
                continue
            admission = DetailsAdmission(request, future, group)
            queue = self.fast_track.admissions if future.fast_track else self.admissions
            queue.add(admission)

    @property
    def admission_queue(self):
        if self.fast_track.admissions and (not self.admissions or self.priority_admissions < self.priority_cap):
            return self.fast_track.admissions
        return self.admissions

    def admit(self):
        while self.can_continue and self.can_admit:
            self.start_read(self.admission_queue.pop())

    def start_read(self, admission):
        admission.future.admission = None
        self.priority_admissions = self.priority_admissions + 1 if admission.fast_track else 0
        self.reads_since_commit += 1
        if admission.future.done():
            return
        if admission.request.cache_refresh == 'force':
            self.lookup(admission.request, admission.future, admission.group, admission.fast_track)
            return
        self.reading += 1
        future = self.reader.submit(self.backend.read_worker, admission.request)
        future.add_done_callback(
            lambda future, admission=admission: self.post_event('read', admission, future),
        )

    def read_completed(self, admission, future):
        """Answer a cached item, or look up a miss. A failed read restarts the service as before."""
        self.reading -= 1
        data = future.result()
        if admission.future.done():
            return
        if data is not None or admission.request.cache_refresh == 'never':
            admission.future.set_result(data)
            return
        # A priority promotion during the read is carried by the future's fast_track flag.
        self.lookup(admission.request, admission.future, admission.group, admission.fast_track)

    def lookup(self, request, future, group, fast_track=False):
        """Share or queue an online lookup for a request that the cache did not answer."""
        lookup = self.backend.lookup(request)
        key = lookup.key
        if key in self.pending:
            job = self.pending[key]
            job.waiters.append((request, future))
            future.job = job
            if fast_track:
                self.promote(job)
            lookup.close()
            return
        job = LookupJob(request, key, (request, future), group, fast_track)
        future.job = job
        self.pending[key] = job
        try:
            dependencies = lookup.factory.get_lookup_dependencies(request)
        finally:
            lookup.close()
        if not dependencies:
            self.make_ready(job)
            return
        job.dependencies = self.submit(dependencies, group=group, fast_track=job.fast_track)
        for dependency in job.dependencies:
            dependency.add_done_callback(
                lambda future, job=job: self.post_event('dependency', job),
            )

    def promote(self, job):
        if job.fast_track:
            return
        job.fast_track = True
        if job.queue is self.ready:
            self.move_queue(job, self.fast_track.ready)
        elif job.queue is self.completed:
            self.move_queue(job, self.fast_track.completed)
        for dependency in job.dependencies:
            self.promote_dependency(dependency)

    def promote_dependency(self, future):
        if future.done():
            return
        future.fast_track = True
        if future.admission is not None and future.admission.queue is self.admissions:
            self.move_queue(future.admission, self.fast_track.admissions)
        if future.job is not None:
            self.promote(future.job)

    @staticmethod
    def move_queue(item, queue):
        item.queue.remove(item)
        queue.add(item)

    def dependency_finished(self, job):
        if job.ready or job.key not in self.pending:
            return
        if not all(future.done() for future in job.dependencies):
            return
        errors = [future.exception() for future in job.dependencies if future.exception()]
        if errors:
            self.fail(job, DetailsLookupError(f'Dependency of {job.request.identity} failed: {errors[0]}'))
            return
        values = [future.result() for future in job.dependencies]
        if not all(values):
            self.finish(job)
            return
        job.parent_data = values[0]
        self.make_ready(job)

    def make_ready(self, job):
        job.ready = True
        # Parent responses can populate child rows, so recheck before fetching.
        if job.request.cache_refresh != 'force' and self.backend.read(job.request) is not None:
            self.finish(job)
            return
        lookup = self.backend.lookup(job.request, job.parent_data)
        try:
            if not lookup.factory.data_cond or not lookup.factory.online_data_cond:
                self.finish(job)
                return
        finally:
            lookup.close()
        queue = self.fast_track.ready if job.fast_track else self.ready
        queue.add(job)

    @property
    def is_commit_backlogged(self):
        """Pause new fetches while finished fetches wait to be written."""
        return len(self.completed) >= 2 * self.batch_size

    @property
    def can_dispatch(self):
        return self.active < self.batch_size and bool(self.dispatch_queue) and not self.stopping

    @property
    def can_dispatch_regular(self):
        return bool(
            self.ready
            and self.active_regular < self.batch_size - self.reserved_workers
            and not self.is_commit_backlogged
        )

    @property
    def dispatch_queue(self):
        fast_ready = self.fast_track.ready and len(self.fast_track.completed) < 2 * self.batch_size
        if fast_ready and (not self.can_dispatch_regular or self.priority_dispatches < self.priority_cap):
            return self.fast_track.ready
        return self.ready if self.can_dispatch_regular else None

    def dispatch(self):
        while self.can_continue and self.can_dispatch:
            self.dispatch_next()

    def dispatch_next(self):
        job = self.dispatch_queue.pop()
        self.priority_dispatches = self.priority_dispatches + 1 if job.fast_track else 0
        # A completed sibling/parent may have populated this queued item.
        if job.request.cache_refresh != 'force' and self.backend.read(job.request) is not None:
            self.finish(job)
            return
        self.start_fetch(job)

    def start_fetch(self, job):
        job.worker_fast_track = job.fast_track
        self.active += 1
        self.active_regular += not job.worker_fast_track
        future = self.executor.submit(self.backend.fetch, job.request, job.parent_data)
        future.add_done_callback(
            lambda future, job=job: self.post_event('fetched', job, future),
        )

    def fetch_completed(self, job, future):
        """Free the worker for the next fetch; the result is committed separately."""
        self.active -= 1
        self.active_regular -= not job.worker_fast_track
        job.fetch_future = future
        queue = self.fast_track.completed if job.fast_track else self.completed
        queue.add(job)

    def is_commit_permitted(self, committed):
        return committed < self.commit_cap and self.can_commit and self.can_continue

    def commit_pending(self):
        self.commit_queue(self.completed)

    def commit_queue(self, queue):
        committed = 0
        while queue and self.is_commit_permitted(committed):
            job = queue.pop()
            self.commit_completed(job, job.fetch_future)
            committed += 1
        if committed:
            self.reads_since_commit = 0

    def commit_completed(self, job, future):
        try:
            self.commit(job, future.result())
        except Exception as exc:
            kodi_log(f'Item detail lookup failed for {job.request.identity}:\n{format_exc()}', 1)
            self.fail(job, DetailsLookupError(f'{job.request.identity}: {exc}'))
            return
        self.finish(job)

    def commit(self, job, queue):
        # User art is cleared on refresh even when the online lookup returned nothing.
        if queue or job.request.clear_user_art:
            self.backend.commit(job.request, queue)

    def finish(self, job):
        del self.pending[job.key]
        for request, future in job.waiters:
            if future.done():
                continue
            data = self.backend.read(request)
            if data is None:
                data = self.backend.fallback(request)
            future.set_result(data)

    def fail(self, job, error):
        del self.pending[job.key]
        for request, future in job.waiters:
            if not future.done():
                future.set_exception(error)

    def fail_waiters(self):
        with self.lock:
            self.stopping = True
            for future in tuple(self.waiters):
                if not future.done():
                    future.set_exception(
                        DetailsServiceUnavailable(
                            f'Item detail service stopped: {self.failure or "restart/shutdown"}',
                        ),
                    )
            self.pending.clear()
            self.admissions.clear()
            self.ready.clear()
            self.completed.clear()
            self.fast_track.clear()

    def stop(self):
        with self.lock:
            self.stopping = True
            self.post_event('stop')
        self.join()
