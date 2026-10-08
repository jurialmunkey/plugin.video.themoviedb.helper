from tmdbhelper.lib.items.directories.lists_default import ListProperties, ListDefault
from tmdbhelper.lib.items.directories.trakt.mapper_stats import HistoryStatsItemMapper, MonthlyHistoryStatsItemMapper
from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class ListHistoryStatsProperties(ListProperties):

    container_content = 'files'
    item_mapper_class = HistoryStatsItemMapper
    item_type = None
    days = 30
    sort_how = 'desc'

    @cached_property
    def sync_data(self):
        return {
            i['watched_date']: i['watched_count']
            for i in self.sync_data_getter.items or ()
        }

    @cached_property
    def sync_data_getter(self):
        return self.get_sync_data_getter()

    def get_sync_data_getter(self):
        return SyncDataFactory(self).get_watched_history_stats_getter(self.item_type, self.days)

    @cached_property
    def total(self):
        return sum(self.watched_counts)

    @cached_property
    def lowest(self):
        return min(self.watched_counts, default=0)

    @cached_property
    def highest(self):
        return max(self.watched_counts, default=0)

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    @cached_property
    def watched_dates(self):
        today = get_datetime_today()
        return [
            (today - get_timedelta(days=day)).strftime('%Y-%m-%d')
            for day in range(self.days)
        ]

    @cached_property
    def watched_counts(self):
        return [self.sync_data.get(watched_date, 0) for watched_date in self.watched_dates]

    @cached_property
    def watched_ranks(self):
        ranks = {}
        for rank, watched_count in enumerate(sorted(self.watched_counts), 1):
            ranks.setdefault(watched_count, rank)
        return ranks

    @cached_property
    def items(self):
        return [
            self.get_mapped_item({
                'watched_date': watched_date,
                'watched_count': watched_count,
                'total': self.total,
                'lowest': self.lowest,
                'highest': self.highest,
                'rank': self.watched_ranks[watched_count],
            })
            for watched_date, watched_count in zip(self.watched_dates, self.watched_counts)
        ]

    @cached_property
    def sorted_items(self):
        if self.sort_how == 'asc':
            return self.filtered_items[::-1]
        return self.filtered_items


class ListMonthlyHistoryStatsProperties(ListHistoryStatsProperties):

    item_mapper_class = MonthlyHistoryStatsItemMapper
    months = 12

    def get_sync_data_getter(self):
        return SyncDataFactory(self).get_watched_monthly_history_stats_getter(self.item_type, self.months)

    @cached_property
    def watched_dates(self):
        today = get_datetime_today()
        month_index = today.year * 12 + today.month - 1
        return [
            today.replace(year=month // 12, month=month % 12 + 1, day=1).strftime('%Y-%m-%d')
            for month in range(month_index, month_index - self.months, -1)
        ]


class ListHistoryStats(ListDefault):

    list_properties_class = ListHistoryStatsProperties
    kodi_db = None

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32194
        list_properties.pagination = False
        return list_properties

    def get_items(self, tmdb_type, days=30, period='day', months=12, sort_how='desc', **kwargs):
        self.list_properties_class = ListMonthlyHistoryStatsProperties if period == 'month' else ListHistoryStatsProperties
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.item_type = 'episode' if tmdb_type == 'tv' else 'movie'
        self.list_properties.days = max(try_int(days) or 30, 1)
        self.list_properties.months = max(try_int(months) or 12, 1)
        self.list_properties.sort_how = sort_how if sort_how in ('asc', 'desc') else 'desc'
        return self.get_items_finalised()
