from threading import Condition
from time import monotonic


class DetailsRatingsProgress:
    """A lookup's ratings so far, for monitors that ask for them before the lookup finishes.

    The lookup updates it once its saved ratings are read and again as each provider finishes
    online. Only providers with values are counted, so a monitor waiting for more than it has
    received is woken only when there is something new to show.
    """

    def __init__(self):
        self.condition = Condition()
        self.ratings = {}  # Every value so far
        self.received = 0  # Providers with values so far
        self.online_time = None  # When the latest values came from online, or None for saved values
        self.is_done = False

    def update(self, ratings, received, is_online):
        with self.condition:
            self.ratings = ratings
            self.received = received
            self.online_time = monotonic() if is_online else self.online_time
            self.condition.notify_all()

    def finish(self, future=None):
        """Called when the lookup ends, including when it is cancelled before it starts."""
        with self.condition:
            self.is_done = True
            self.condition.notify_all()

    def wait_for_more(self, received, timeout):
        """Whether more providers than received have values, or the lookup ended, before the timeout."""
        with self.condition:
            return self.condition.wait_for(lambda: self.is_done or self.received > received, timeout)

    def wait_for_done(self, timeout):
        with self.condition:
            return self.condition.wait_for(lambda: self.is_done, timeout)

    def get_gather_time(self, gather_time):
        """How much longer to wait for providers that finish soon after the latest online values."""
        with self.condition:
            if self.online_time is None:
                return 0
            return max(self.online_time + gather_time - monotonic(), 0)

    def get_snapshot(self):
        """The values so far and the count of providers they came from, read together."""
        with self.condition:
            return (self.ratings, self.received)
