from concurrent.futures import CancelledError, Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from tmdbhelper.lib.items.database.details.protocol import DetailsLookupError
from tmdbhelper.lib.items.database.details.ratings.progress import DetailsRatingsProgress


class DetailsRatingsJob:
    """An item's ratings lookup on a lane, with the progress that partial requests wait on."""

    def __init__(self, item):
        self.item = item
        self.progress = DetailsRatingsProgress()
        self.future = None

    def submit(self, lane, func):
        """Run func(self) on the lane. Progress finishes when the lookup ends or is cancelled."""
        self.future = lane.submit(func, self)
        self.future.add_done_callback(self.progress.finish)

    def set_result(self, ratings):
        """Ratings that are already known, so that no lookup is needed."""
        self.future = Future()
        self.future.set_result(ratings)
        self.progress.finish()

    def cancel(self):
        """Only a lookup that has not started is cancelled."""
        self.future.cancel()

    def get_result(self, timeout):
        """The lookup's ratings. A replaced lookup has none, as its item is no longer shown."""
        try:
            return self.future.result(timeout=timeout)
        except CancelledError:
            return {}
        except FutureTimeoutError:
            raise DetailsLookupError('Item ratings lookup timed out')
        except Exception as exc:
            raise DetailsLookupError(f'Item ratings lookup failed: {exc}')
