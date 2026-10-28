import re
from tmdbhelper.lib.sync.itemlist import ItemListSyncDataWatched


class WatchedOnDateParts:
    """Normalize URL date components to SQLite STRFTIME values."""

    month_names = (
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
    )
    weekday_names = (
        'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
    )

    def __init__(self, day=None, month=None, year=None):
        if day is None and month is None and year is None:
            raise ValueError('sync_watchedon requires at least one of day, month, or year')
        self.year = self.get_year(year)
        self.month = self.get_month(month)
        self.day, self.weekday = self.get_day(day)

    @staticmethod
    def get_number(value, name, minimum, maximum):
        if not re.fullmatch(r'[0-9]+', value) or not minimum <= int(value) <= maximum:
            raise ValueError(f'{name} must be a number from {minimum} to {maximum}')
        return int(value)

    @staticmethod
    def get_named_number(value, names, start):
        numbers = {
            key: number
            for number, name in enumerate(names, start)
            for key in (name, name[:3])
        }
        try:
            return numbers[value.lower()]
        except KeyError:
            raise ValueError(f'Invalid English date name: {value}') from None

    def get_year(self, value):
        if value is None:
            return None
        value = str(value)
        if len(value) != 4:
            raise ValueError('year must have four digits')
        return str(self.get_number(value, 'year', 1000, 9999))

    def get_month(self, value):
        if value is None:
            return None
        value = str(value)
        if re.fullmatch(r'[0-9]+', value):
            return f"{self.get_number(value, 'month', 1, 12):02d}"
        return f'{self.get_named_number(value, self.month_names, 1):02d}'

    def get_day(self, value):
        if value is None:
            return (None, None)
        value = str(value)
        if re.fullmatch(r'[0-9]+', value):
            return (f"{self.get_number(value, 'day', 1, 31):02d}", None)
        return (None, str(self.get_named_number(value, self.weekday_names, 0)))


class ItemListSyncDataWatchedOn(ItemListSyncDataWatched):
    """Use the standard watched-item mapping and sorting for a date selection."""

    def get_watched_on_getter(self, item_type):
        return self.syncdata.get_watched_on_getter(item_type, self.watched_on)

    def get_items(self):
        return self.make_list(self.get_watched_on_getter)
