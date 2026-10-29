from queue import Empty, Queue


class CalendarFetchProgress:
    """Queue day-worker progress for delivery on the calling thread."""

    def __init__(self, dates, callback):
        self.callback = callback
        self.days = {date: 0 for date in dates}
        self.events = Queue()

    def report(self, date, status, page=0, pages=0):
        self.events.put((date, status, page, pages))

    def drain(self):
        while True:
            try:
                event = self.events.get_nowait()
            except Empty:
                return
            self.update(*event)

    def update(self, date, status, page, pages):
        if status in ('cached', 'complete'):
            self.days[date] = 1
        elif status == 'page':
            # Reserve the final fraction until the complete day is committed.
            self.days[date] = page / (pages + 1)
        if self.callback:
            self.callback(
                int(100 * sum(self.days.values()) / len(self.days)),
                date)
