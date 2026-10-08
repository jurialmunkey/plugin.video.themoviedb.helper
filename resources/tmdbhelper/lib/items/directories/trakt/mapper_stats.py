from tmdbhelper.lib.items.directories.trakt.mapper_basic import ItemMapper
from tmdbhelper.lib.addon.plugin import get_infolabel
from tmdbhelper.lib.addon.tmdate import convert_timestamp, format_date_obj
from jurialmunkey.ftools import cached_property


class HistoryStatsItemMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.meta['watched_date']

    @cached_property
    def watched_date(self):
        return convert_timestamp(self.label, time_fmt='%Y-%m-%d', time_lim=10)

    @cached_property
    def watched_count(self):
        return self.meta['watched_count']

    @cached_property
    def total(self):
        return self.meta['total']

    @cached_property
    def percent(self):
        if not self.total:
            return 0
        return self.watched_count * 100 // self.total

    @cached_property
    def label2(self):
        return f'{self.watched_count}'

    def get_infolabels(self):
        return {'title': self.label}

    def get_infoproperties(self):
        return {
            'watched_count': self.watched_count,
            'count': self.watched_count,
            'total': self.total,
            'percent': self.percent,
            'long': format_date_obj(self.watched_date, region_fmt='datelong'),
            'short': format_date_obj(self.watched_date, '%d %b'),
            'day': format_date_obj(self.watched_date, '%A'),
            'day_short': format_date_obj(self.watched_date, '%a'),
            'year': format_date_obj(self.watched_date, '%Y'),
            'custom': format_date_obj(self.watched_date, get_infolabel('Skin.String(TMDbHelper.Date.Format)') or '%d %b %Y'),
            'month': format_date_obj(self.watched_date, '%B'),
            'month_short': format_date_obj(self.watched_date, '%b'),
            'month_number': self.watched_date.month,
            'day_number': self.watched_date.day,
            'week_number': (self.watched_date.day - 1) // 7 + 1,
        }

    def get_item(self):
        item = super().get_item()
        item['label2'] = self.label2
        item['is_folder'] = False
        return item
