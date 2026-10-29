from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import convert_timestamp, get_region_date
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.items.directories.lists_calendar import CalendarItemStacker


class LibraryCalendarItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.meta['label']

    @cached_property
    def air_date(self):
        return convert_timestamp(self.meta['infolabels']['premiered'], time_fmt='%Y-%m-%d')

    def get_infolabels(self):
        return dict(self.meta['infolabels'])

    def get_infoproperties(self):
        return dict(self.meta['infoproperties'], **{
            'air_date': get_region_date(self.air_date, 'datelong'),
            'air_day': self.air_date.strftime('%A'),
            'air_day_short': self.air_date.strftime('%a'),
            'air_date_short': self.air_date.strftime('%d %b'),
        })

    def get_unique_ids(self):
        return dict(self.meta['unique_ids'])

    def get_params(self):
        return dict(self.meta['params'])

    def get_art(self):
        return dict(self.meta['art'])


class LibraryCalendarItemStacker(CalendarItemStacker):
    def get_item_id(self, item):
        return (item['unique_ids']['tvshow.tmdb'], item['infolabels']['premiered'])
