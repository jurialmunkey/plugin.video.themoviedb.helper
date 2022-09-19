
from xbmc import Monitor
from threading import Thread
from resources.lib.addon.plugin import get_setting, encode_url
from resources.lib.addon.logger import kodi_log
from resources.lib.addon.tmdate import set_timestamp, get_timestamp
from resources.lib.addon.window import get_property


def has_property_lock(property_name, timeout=5, polling=0.05):
    """ Checks for a window property lock and wait for it to be cleared before continuing
    Returns True after property clears if was locked
    """
    if not get_property(property_name):
        return False
    monitor = Monitor()
    timeend = set_timestamp(timeout)
    timeexp = True
    while not monitor.abortRequested() and get_property(property_name) and timeexp:
        monitor.waitForAbort(polling)
        timeexp = get_timestamp(timeend)
    if not timeexp:
        kodi_log(f'{property_name} Timeout!', 1)
    del monitor
    return True


def use_thread_lock(property_name, timeout=10, polling=0.05, combine_name=False):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            name = encode_url(f"{property_name}.{'.'.join(args)}", **kwargs) if combine_name else property_name
            if not has_property_lock(name, timeout, polling):  # Check if locked and wait if it is
                get_property(name, 1)  # Lock thread for others
            response = func(self, *args, **kwargs)  # Get our response
            get_property(name, clear_property=True)  # Unlock for other threads
            return response
        return wrapper
    return decorator


class ParallelThread():
    def __init__(self, items, func, *args, **kwargs):
        """ ContextManager for running parallel threads alongside another function
        with ParallelThread(items, func, *args, **kwargs) as pt:
            pass
            item_queue = pt.queue
        item_queue[x]  # to get returned items
        """
        mon = Monitor()
        thread_max = get_setting('max_threads', mode='int') or len(items)
        self.queue = [None] * len(items)
        self._pool = [None] * thread_max
        self._exit = False
        for x, i in enumerate(items):
            n = x
            while n >= thread_max and not mon.abortRequested():  # Hit our thread limit so look for a spare spot in the queue
                for y, j in enumerate(self._pool):
                    if j.is_alive():
                        continue
                    n = y
                    break
                if n >= thread_max:
                    mon.waitForAbort(0.025)
            try:
                self._pool[n] = Thread(target=self._threadwrapper, args=[x, i, func, *args], kwargs=kwargs)
                self._pool[n].start()
            except IndexError:
                kodi_log(f'ParallelThread: INDEX {n} OUT OF RANGE {thread_max}', 1)

    def _threadwrapper(self, x, i, func, *args, **kwargs):
        self.queue[x] = func(i, *args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for i in self._pool:
            if self._exit:
                break
            try:
                i.join()
            except AttributeError:  # is None
                pass
