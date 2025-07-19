from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from jurialmunkey.ftools import cached_property


class BaseDirItemCalendarLastFornight(BaseDirItem):
    priority = 100
    label_type = 'localize'
    label_localized = 32280
    params = {'startdate': -14, 'days': 14}
    types = ('movie', 'tv', )
    art_icon = 'resources/icons/trakt/calendar.png'


class BaseDirItemCalendarLastWeek(BaseDirItemCalendarLastFornight):
    priority = 110
    label_localized = 32281
    params = {'startdate': -7, 'days': 7}


class BaseDirItemCalendarYesterday(BaseDirItemCalendarLastFornight):
    priority = 120
    label_localized = 32282
    params = {'startdate': -1, 'days': 1}


class BaseDirItemCalendarToday(BaseDirItemCalendarLastFornight):
    priority = 130
    label_localized = 33006
    params = {'startdate': 0, 'days': 1}


class BaseDirItemCalendarTomorrow(BaseDirItemCalendarLastFornight):
    priority = 140
    label_localized = 33007
    params = {'startdate': 1, 'days': 1}


class BaseDirItemCalendarDay2(BaseDirItemCalendarLastFornight):
    priority = 150
    startdate = 2

    @cached_property
    def params(self):
        return {'startdate': self.startdate, 'days': 1}

    @cached_property
    def date(self):
        from tmdbhelper.lib.addon.tmdate import get_timedelta, get_datetime_today
        return get_datetime_today() + get_timedelta(days=self.startdate)

    @cached_property
    def label(self):
        return self.date.strftime('%A')


class BaseDirItemCalendarDay3(BaseDirItemCalendarDay2):
    priority = 160
    startdate = 3


class BaseDirItemCalendarDay4(BaseDirItemCalendarDay2):
    priority = 170
    startdate = 4


class BaseDirItemCalendarDay5(BaseDirItemCalendarDay2):
    priority = 180
    startdate = 5


class BaseDirItemCalendarDay6(BaseDirItemCalendarDay2):
    priority = 190
    startdate = 6


class BaseDirItemCalendarNextWeek(BaseDirItemCalendarLastFornight):
    priority = 200
    label_localized = 32284
    params = {'startdate': 0, 'days': 7}


class BaseDirItemCalendarNextFortnight(BaseDirItemCalendarLastFornight):
    priority = 210
    label_localized = 32285
    params = {'startdate': 0, 'days': 14}


def configure(i, **params):
    instance = i()
    instance.params.update(params)
    return instance


def get_all_calendar_class_instances(**params):
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [configure(i, **params) for i in get_all_module_class_objects_by_priority(__name__)]
