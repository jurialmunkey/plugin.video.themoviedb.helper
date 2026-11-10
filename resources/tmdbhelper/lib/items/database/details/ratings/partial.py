from tmdbhelper.lib.items.database.details.protocol import DetailsLookupError


class DetailsRatingsPartial:
    """A monitor's reply while an item's ratings lookup runs.

    The reply waits until more providers have values than the monitor has received. Saved
    ratings are returned as soon as they are read. Online ratings wait briefly, so that
    providers finishing at about the same time arrive together. Each reply has every value
    so far, so that the monitor can replace what it set, with the count of providers to ask
    again with. It is complete once the lookup ends.
    """

    gather_time = 0.2  # Seconds to wait for other providers after online values arrive

    def __init__(self, job, received, timeout):
        self.job = job
        self.received = received
        self.timeout = timeout

    @property
    def progress(self):
        return self.job.progress

    @property
    def reply(self):
        return self.get_reply()

    def get_reply(self):
        if not self.progress.wait_for_more(self.received, self.timeout):
            raise DetailsLookupError('Item ratings lookup timed out')
        self.progress.wait_for_done(self.progress.get_gather_time(self.gather_time))
        if self.progress.is_done:
            return self.get_complete_reply()
        return self.get_partial_reply()

    def get_complete_reply(self):
        """The lookup's own result, which has every provider, or none when it was replaced."""
        received = self.progress.get_snapshot()[1]
        return {'ratings': self.job.get_result(0), 'received': received, 'complete': True}

    def get_partial_reply(self):
        ratings, received = self.progress.get_snapshot()
        return {'ratings': ratings, 'received': received, 'complete': False}
