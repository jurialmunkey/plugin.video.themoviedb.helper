"""A small thread pool whose threads each keep their own database connections."""

from concurrent.futures import Future
from contextlib import ExitStack
from queue import SimpleQueue
from threading import Lock, Thread
from tmdbhelper.lib.files.dbconnection import DatabaseHold


class DatabaseWork:
    """A call submitted to a DatabaseWorkerPool and the future that receives its result."""

    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.future = Future()

    def run(self, worker):
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            worker.hold()
            result = self.func(*self.args, **self.kwargs)
        except BaseException as exc:
            self.future.set_exception(exc)
            return
        self.future.set_result(result)


class DatabaseWorker(Thread):
    """A pool thread that holds its connections from its first call until it stops.
    A failed connection fails that call, and the next call tries again."""

    def __init__(self, pool, name):
        super().__init__(name=name)
        self.pool = pool
        self.connections = None
        self.is_holding = False

    def run(self):
        with ExitStack() as self.connections:
            for work in iter(self.pool.queue.get, None):
                work.run(self)

    def hold(self):
        if self.is_holding:
            return
        self.connections.enter_context(DatabaseHold(*self.pool.databases))
        self.is_holding = True


class DatabaseWorkerPool:
    """Run calls on up to max_workers threads that keep their own connections to the
    databases for their lifetime, and close them on their own thread at shutdown.

    Only small pools should hold connections for their lifetime; larger pools open a
    session for each task instead. Threads start as calls are submitted, as they do in
    ThreadPoolExecutor, whose submit() and shutdown() this follows.
    """

    def __init__(self, databases, max_workers=1, thread_name_prefix='TMDbHelper database'):
        self.databases = databases
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.queue = SimpleQueue()
        self.lock = Lock()
        self.workers = []
        self.is_shutdown = False

    def submit(self, func, *args, **kwargs):
        work = DatabaseWork(func, args, kwargs)
        with self.lock:
            if self.is_shutdown:
                raise RuntimeError('Cannot schedule new calls after shutdown')
            self.queue.put(work)
            self.start_worker()
        return work.future

    def start_worker(self):
        if len(self.workers) >= self.max_workers:
            return
        worker = DatabaseWorker(self, f'{self.thread_name_prefix}_{len(self.workers)}')
        self.workers.append(worker)
        worker.start()

    def shutdown(self, wait=True):
        """Calls already submitted still run; each worker then closes its connections."""
        with self.lock:
            self.is_shutdown = True
            for worker in self.workers:
                self.queue.put(None)
        if not wait:
            return
        for worker in self.workers:
            worker.join()
