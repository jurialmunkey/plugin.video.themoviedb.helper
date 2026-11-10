"""Queue state for cached batches, online misses and fast-track lookups."""

from collections import OrderedDict, deque
from concurrent.futures import Future
from jurialmunkey.ftools import cached_property


class DetailsFuture(Future):
    def __init__(self, fast_track):
        super().__init__()
        self.fast_track = fast_track
        self.admission = None
        self.job = None

    def clear_lookup(self):
        self.admission = None
        self.job = None


class DetailsAdmission:
    def __init__(self, request, future, group):
        self.request = request
        self.future = future
        self.group = group
        self.queue = None
        self.future.admission = self

    @property
    def fast_track(self):
        return self.future.fast_track


class DetailsGroupedQueue:
    """Keep each group's items together until the queue's policy rotates it."""

    def __init__(self):
        self.groups = OrderedDict()

    def __bool__(self):
        return bool(self.groups)

    def __len__(self):
        return sum(len(items) for items in self.groups.values())

    @property
    def group_count(self):
        return len(self.groups)

    def add(self, item):
        self.groups.setdefault(item.group, deque()).append(item)
        item.queue = self

    def pop(self):
        group, items = self.groups.popitem(last=False)
        item = items.popleft()
        if items:
            self.requeue_group(group, items)
        item.queue = None
        return item

    def requeue_group(self, group, items):
        self.groups[group] = items
        self.groups.move_to_end(group, last=False)

    def remove(self, item):
        items = self.groups[item.group]
        items.remove(item)
        if not items:
            del self.groups[item.group]
        item.queue = None

    def clear(self):
        self.groups.clear()


class DetailsAdmissionQueue(DetailsGroupedQueue):
    """Cached batch checks retain arrival order within and between batches."""


class DetailsOnlineQueue(DetailsGroupedQueue):
    """Online misses take turns between batches."""

    def requeue_group(self, group, items):
        self.groups[group] = items


class DetailsCommitQueue:
    def __init__(self):
        self.items = deque()

    def __bool__(self):
        return bool(self.items)

    def __len__(self):
        return len(self.items)

    def add(self, job):
        self.items.append(job)
        job.queue = self

    def pop(self):
        job = self.items.popleft()
        job.queue = None
        return job

    def remove(self, job):
        self.items.remove(job)
        job.queue = None

    def clear(self):
        self.items.clear()


class DetailsFastTrackQueue:
    """A priority lane through admission, online fetching and result commits."""

    @cached_property
    def admissions(self):
        return self.get_admissions()

    def get_admissions(self):
        return DetailsAdmissionQueue()

    @cached_property
    def ready(self):
        return self.get_ready()

    def get_ready(self):
        return DetailsOnlineQueue()

    @cached_property
    def completed(self):
        return self.get_completed()

    def get_completed(self):
        return DetailsCommitQueue()

    def clear(self):
        self.admissions.clear()
        self.ready.clear()
        self.completed.clear()

