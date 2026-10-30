"""Calendar-based refresh policy, independent of Kodi and network access."""
from calendar import monthrange
from datetime import date


class CollectionRefreshPolicy:
    intervals = ((4, 1), (8, 3), (16, 6))

    @staticmethod
    def add_months(value, months):
        year, month = divmod(value.year * 12 + value.month - 1 + months, 12)
        month += 1
        return value.replace(year=year, month=month, day=min(value.day, monthrange(year, month)[1]))

    @staticmethod
    def get_release_date(value):
        return date.fromisoformat(value) if value else None

    def get_interval(self, release_dates, today):
        dates = tuple(self.get_release_date(value) for value in release_dates)
        if not dates or None in dates or max(dates) > today:
            return 1  # Unknown or upcoming members need relatively frequent checks.
        latest = max(dates)
        return next(
            (months for years, months in self.intervals if today < self.add_months(latest, years * 12)),
            12)

    def get_next_check(self, checked_at, release_dates, today):
        checked_date = date.fromisoformat(checked_at[:10])
        return self.add_months(checked_date, self.get_interval(release_dates, today))
