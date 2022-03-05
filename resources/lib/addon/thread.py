from threading import Thread


class ParallelThread():
    def __init__(self, items, func, *args, **kwargs):
        """ ContextManager for running parallel threads alongside another function
        with ParallelThread(items, func, *args, **kwargs) as pt:
            pass
            item_queue = pt.queue
        item_queue[x]  # to get returned items
        """
        self.queue = [None] * len(items)
        self._pool = [None] * len(items)
        for x, i in enumerate(items):
            self._pool[x] = Thread(target=self._threadwrapper, args=[x, i, func, *args], kwargs=kwargs)
            self._pool[x].start()

    def _threadwrapper(self, x, i, func, *args, **kwargs):
        self.queue[x] = func(i, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for i in self._pool:
            i.join()
