from collections import deque
from concurrent.futures import ThreadPoolExecutor
from xbmc import Monitor
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import TimerList
from tmdbhelper.lib.addon.thread import ParallelThread


class ListItemWriter:
    def __init__(self, items, connection, timer_lists, log_timers=False):
        self.items = items
        self.connection = connection
        self.timer_lists = timer_lists
        self.log_timers = log_timers
        self.monitor = Monitor()
        self.pending = deque()
        self.write_timers = {}
        self.has_written_data = False
        self.aborted = False

    @cached_property
    def max_workers(self):
        return ParallelThread.thread_max or len(self.items)

    def get_item_queue(self, item):
        if self.monitor.abortRequested():
            return
        return item.try_queued_data()

    def submit_items(self, executor):
        for item in self.items:
            self.pending.append((item, executor.submit(self.get_item_queue, item)))

    def cancel_pending(self):
        for _, future in self.pending:
            future.cancel()

    def stop_if_aborted(self):
        if not self.monitor.abortRequested():
            return False
        self.aborted = True
        self.cancel_pending()
        return True

    def write_items(self):
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                try:
                    self.submit_items(executor)
                    self.write_pending_items()
                except BaseException:
                    self.cancel_pending()
                    raise
        finally:
            self.set_write_timers()

    def write_pending_items(self):
        while self.pending:
            if self.stop_if_aborted():
                return
            _, future = self.pending[0]
            func_queue = future.result()  # Wait without holding the SQLite writer lock.
            if self.stop_if_aborted():
                return
            if not func_queue:
                self.pending.popleft()
                continue
            if not self.write_ready_items():
                self.cancel_pending()
                return

    def set_ready_items(self):
        while self.pending and self.pending[0][1].done():
            if self.stop_if_aborted():
                return False
            item, future = self.pending.popleft()
            func_queue = future.result()
            if not func_queue:
                continue
            with TimerList(self.write_timers, ' - writer', log_threshold=0, logging=self.log_timers):
                item.set_queued_data(self.connection, func_queue)
        return not self.stop_if_aborted()

    def write_ready_items(self):
        existing_connection = bool(self.connection.open_connection)
        try:
            with self.connection.open():
                return self.write_transaction()
        finally:
            if not existing_connection:
                self.connection.close()

    def write_transaction(self):
        cursor = self.connection.open_connection
        cursor.execute('BEGIN')
        try:
            if not self.set_ready_items():
                cursor.execute('ROLLBACK')
                return False
            with TimerList(self.write_timers, ' - commit', log_threshold=0, logging=self.log_timers):
                cursor.execute('COMMIT')
        except BaseException:
            cursor.execute('ROLLBACK')
            raise
        self.has_written_data = True
        return True

    def set_write_timers(self):
        if not self.log_timers:
            return
        for name in (' - writer', ' - commit'):
            values = self.write_timers.get(name, ())
            self.timer_lists.setdefault(name, []).append(sum(values))
