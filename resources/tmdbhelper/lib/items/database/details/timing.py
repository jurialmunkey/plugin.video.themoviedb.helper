"""Per-batch stage timings returned to the list for its timer report."""

from contextlib import contextmanager
from time import perf_counter
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.details.coordinator import DetailsCoordinator
from tmdbhelper.lib.items.database.details.service import DetailsRequestHandler


class DetailsStageTimer:
    """Wall time during which at least one operation of a stage was running."""

    def __init__(self):
        self.active = 0
        self.started = 0
        self.total = 0

    def start(self):
        if not self.active:
            self.started = perf_counter()
        self.active += 1

    def stop(self):
        self.active -= 1
        if not self.active:
            self.total += perf_counter() - self.started


class DetailsBatchTimings:
    """Stage timings for one batch. Stages overlap, so their totals are not cumulative.

    The handler thread times sync before submitting the batch. The coordinator thread
    times cached reads, online calls and saves, including the batch's dependencies.
    Work shared with an earlier batch is timed in that batch.
    """

    stage_names = ('sync', 'read', 'call', 'save')

    @cached_property
    def stage_timers(self):
        return self.get_stage_timers()

    def get_stage_timers(self):
        return {name: DetailsStageTimer() for name in self.stage_names}

    def start_stage(self, name):
        self.stage_timers[name].start()

    def stop_stage(self, name):
        self.stage_timers[name].stop()

    @contextmanager
    def measure_stage(self, name):
        self.start_stage(name)
        try:
            yield
        finally:
            self.stop_stage(name)

    @property
    def summary(self):
        return {name: timer.total for name, timer in self.stage_timers.items()}


class TimedDetailsCoordinator(DetailsCoordinator):
    """Time each batch's cached reads, online calls and saves against its group."""

    def start_read(self, admission):
        reading = self.reading
        super().start_read(admission)
        # Requests already answered or forced online start no read.
        if self.reading > reading:
            admission.group.start_stage('read')

    def read_completed(self, admission, future):
        admission.group.stop_stage('read')
        return super().read_completed(admission, future)

    def start_fetch(self, job):
        job.group.start_stage('call')
        return super().start_fetch(job)

    def fetch_completed(self, job, future):
        job.group.stop_stage('call')
        return super().fetch_completed(job, future)

    def commit(self, job, queue):
        with job.group.measure_stage('save'):
            return super().commit(job, queue)


class TimedDetailsRequestHandler(DetailsRequestHandler):
    """Return the batch's stage timings with its items."""

    def get_batch_timings(self):
        return DetailsBatchTimings()

    def get_batch_response(self, entries, message):
        self.batch_timings = self.get_batch_timings()
        response = super().get_batch_response(entries, message)
        response['timings'] = self.batch_timings.summary
        return response

    def wait_for_sync(self, requests, deadline):
        with self.batch_timings.measure_stage('sync'):
            return super().wait_for_sync(requests, deadline)

    def submit_requests(self, requests):
        return self.server.coordinator.submit(requests, group=self.batch_timings)
