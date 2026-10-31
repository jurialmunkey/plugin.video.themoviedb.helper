from collections import OrderedDict, deque
from concurrent.futures import Future, ThreadPoolExecutor
from queue import Empty, Queue
from threading import RLock, Thread
from traceback import format_exc
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.items.database.details.backend import DetailsBackend
from tmdbhelper.lib.items.database.details.protocol import DetailsLookupError, DetailsServiceUnavailable


class LookupJob:
    def __init__(self, request, key, waiter, group):
        self.request = request
        self.key = key
        self.waiters = [waiter]
        self.dependencies = []
        self.parent_data = None
        self.ready = False
        self.group = group


class DetailsCoordinator(Thread):
    """One cache/commit owner and at most twenty independent online lookups."""

    batch_size = 20

    def __init__(self, backend_class=DetailsBackend):
        super().__init__(name='TMDbHelper item details')
        self.backend_class = backend_class
        self.events = Queue()
        self.pending = {}
        self.admissions = OrderedDict()
        self.ready = OrderedDict()
        self.active = 0
        self.failure = None
        self.lock = RLock()
        self.waiters = set()
        self.stopping = False

    def submit(self, requests, group=None):
        if not requests:
            return []
        futures = [Future() for request in requests]
        with self.lock:
            if self.stopping:
                for future in futures:
                    future.set_exception(DetailsServiceUnavailable('Item detail service is restarting'))
                return futures
            for future in futures:
                self.waiters.add(future)
                future.add_done_callback(self.remove_waiter)
            self.events.put(('submit', deque(zip(requests, futures)), group or object()))
        return futures

    def remove_waiter(self, future):
        with self.lock:
            self.waiters.discard(future)

    def get_batch(self):
        if self.admissions:
            batch = []
        else:
            batch = [self.events.get()]
        for _ in range(self.batch_size - 1):
            try:
                batch.append(self.events.get_nowait())
            except Empty:
                break
        return batch

    def run(self):
        self.backend = None
        self.executor = None
        try:
            self.backend = self.backend_class()
            self.executor = ThreadPoolExecutor(
                max_workers=self.batch_size, thread_name_prefix='TMDbHelper lookup')
            while not self.stopping:
                batch = self.get_batch()
                if self.stopping:
                    break
                with self.backend.connection.open():
                    for event in batch:
                        self.process_event(*event)
                    self.admit()
                    self.dispatch()
        except BaseException as exc:
            self.failure = exc
            kodi_log(f'Item detail lookup failed:\n{format_exc()}', 1)
        finally:
            self.fail_waiters()
            if self.executor is not None:
                # A hung online lookup must not delay the restart. Late results
                # are discarded because nothing reads the event queue any more.
                self.executor.shutdown(wait=False)
            if self.backend is not None:
                self.backend.close()

    def process_event(self, kind, *args):
        if kind == 'submit':
            items, group = args
            self.admissions.setdefault(group, deque()).extend(items)
        elif kind == 'dependency':
            self.dependency_finished(*args)
        elif kind == 'fetched':
            self.fetched(*args)

    def admit(self):
        for _ in range(self.batch_size):
            if not self.admissions:
                return
            group, items = self.admissions.popitem(last=False)
            request, future = items.popleft()
            if items:
                self.admissions[group] = items
            self.lookup(request, future, group)

    def lookup(self, request, future, group):
        if future.done():
            return
        if request.cache_refresh != 'force':
            data = self.backend.read(request)
            if data is not None or request.cache_refresh == 'never':
                future.set_result(data)
                return
        lookup = self.backend.lookup(request)
        key = lookup.key
        if key in self.pending:
            self.pending[key].waiters.append((request, future))
            lookup.close()
            return
        job = LookupJob(request, key, (request, future), group)
        self.pending[key] = job
        try:
            dependencies = lookup.factory.get_lookup_dependencies(request)
        finally:
            lookup.close()
        if not dependencies:
            self.make_ready(job)
            return
        job.dependencies = self.submit(dependencies, group=group)
        for dependency in job.dependencies:
            dependency.add_done_callback(
                lambda future, job=job: self.events.put(('dependency', job)))

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
        self.ready.setdefault(job.group, deque()).append(job)

    def dispatch(self):
        while self.ready and self.active < self.batch_size and not self.stopping:
            group, jobs = self.ready.popitem(last=False)
            job = jobs.popleft()
            if jobs:
                self.ready[group] = jobs
            # A completed sibling/parent may have populated this queued item.
            if job.request.cache_refresh != 'force' and self.backend.read(job.request) is not None:
                self.finish(job)
                continue
            self.active += 1
            future = self.executor.submit(self.backend.fetch, job.request, job.parent_data)
            future.add_done_callback(
                lambda future, job=job: self.events.put(('fetched', job, future)))

    def fetched(self, job, future):
        self.active -= 1
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
                    future.set_exception(DetailsServiceUnavailable(
                        f'Item detail service stopped: {self.failure or "restart/shutdown"}'))

    def stop(self):
        with self.lock:
            self.stopping = True
            self.events.put(('stop', ))
        self.join()
