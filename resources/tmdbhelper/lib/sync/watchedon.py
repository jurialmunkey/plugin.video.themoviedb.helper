import re
from calendar import monthrange
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta
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
        self.year, self.month = self.get_year_month(year, month)
        if self.is_relative_value(day):
            self.year, self.month, self.day = self.get_relative_day(day)
            self.weekday = None
            return
        self.day, self.weekday = self.get_day(day)

    @cached_property
    def today(self):
        return self.get_today()

    def get_today(self):
        return get_datetime_today()

    @staticmethod
    def is_relative_value(value):
        return bool(re.fullmatch(r'-?[0-9]+', str(value))) and int(value) <= 0

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
        if self.is_relative_value(value):
            value = self.today.year + int(value)
        value = str(value)
        if len(value) != 4:
            raise ValueError('year must have four digits')
        return str(self.get_number(value, 'year', 1000, 9999))

    def get_year_month(self, year, month):
        year = self.get_year(year)
        if not self.is_relative_value(month):
            return (year, self.get_month(month))
        month_index = (int(year) if year is not None else self.today.year) * 12 + self.today.month - 1
        year, month = divmod(month_index + int(month), 12)
        year = self.get_number(str(year), 'year', 1000, 9999)
        return (str(year), f'{month + 1:02d}')

    def get_relative_day(self, value):
        year = int(self.year) if self.year is not None else self.today.year
        month = int(self.month) if self.month is not None else self.today.month
        day = min(self.today.day, monthrange(year, month)[1])
        reference_date = self.today.replace(year=year, month=month, day=day)
        watched_date = reference_date + get_timedelta(days=int(value))
        year = self.get_number(str(watched_date.year), 'year', 1000, 9999)
        return (str(year), f'{watched_date.month:02d}', f'{watched_date.day:02d}')

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

    def make_item(self, item):
        entry = super().make_item(item)
        entry['last_watched_at'] = item.item['last_watched_at']
        return entry
