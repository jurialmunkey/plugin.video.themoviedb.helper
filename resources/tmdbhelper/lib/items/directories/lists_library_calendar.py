from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.dialog import DialogProgressSyncBG
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.addon.tmdate import get_calendar_name, get_datetime_today, get_timedelta
from tmdbhelper.lib.calendar.getter import CalendarDataGetter
from tmdbhelper.lib.items.database.baseview_factories.factory import BaseViewFactory
from tmdbhelper.lib.items.directories.lists_default import ListDefault, ListSliceProperties
from tmdbhelper.lib.items.directories.mapper_library_calendar import (
    LibraryCalendarItemMapper,
    LibraryCalendarItemStacker,
)


class ListLibraryCalendarProperties(ListSliceProperties):
    item_mapper_class = LibraryCalendarItemMapper
    container_content = 'episodes'

    @cached_property
    def start_date(self):
        return (get_datetime_today() + get_timedelta(days=self.startdate)).strftime('%Y-%m-%d')

    @cached_property
    def end_date(self):
        return (get_datetime_today() + get_timedelta(days=self.startdate + self.days)).strftime('%Y-%m-%d')

    @cached_property
    def plugin_category(self):
        return get_calendar_name(startdate=self.startdate, days=self.days)

    def get_library_tmdb_id(self, item):
        return try_int(item.get('tmdb_id') or self.query_database.get_tmdb_id(
            tmdb_type='tv', imdb_id=item.get('imdb_id'), tvdb_id=item.get('tvdb_id'),
            query=item.get('showtitle') or item.get('title'), year=item.get('year')))

    @cached_property
    def library_shows(self):
        return self.get_library_shows()

    def get_library_shows(self):
        items = self.kodi_db.database or []
        shows = {}
        for item in items:
            self.update_progress(0, item['title'])
            shows[self.get_library_tmdb_id(item)] = item
        return shows

    @cached_property
    def library_ids(self):
        return set(self.library_shows) - {0}

    @cached_property
    def dropped_ids(self):
        from tmdbhelper.lib.sync.datasync import SyncDataFactory
        getter = SyncDataFactory().get_all_dropped_shows_getter('show')
        return {try_int(item['tmdb_id']) for item in getter.items if item}

    def update_progress(self, percentage, message):
        self.dialog_progress_bg.update(percentage, message=message)

    def update_calendar_progress(self, percentage, message):
        self.update_progress(int(percentage * 0.8), message)

    def get_calendar_items(self):
        getter = CalendarDataGetter()
        getter.start_date = self.start_date
        getter.end_date = self.end_date
        getter.progress_callback = self.update_calendar_progress
        getter.max_workers = min(
            CalendarDataGetter.max_workers,
            max(1, get_setting('max_threads', 'int') or CalendarDataGetter.max_workers))
        getter.discover.tmdb_api = self.tmdb_api
        return getter.items

    def get_show_items(self, tmdb_id):
        view = BaseViewFactory('calendar', 'tv', tmdb_id)
        view.start_date = self.start_date
        view.end_date = self.end_date
        return view.data or []

    def get_mapped_show_items(self, tmdb_id):
        return [self.get_mapped_item(item) for item in self.get_show_items(tmdb_id)]

    def get_library_episode_items(self, matches):
        items = []
        for index, tmdb_id in enumerate(matches, 1):
            title = self.library_shows[tmdb_id]['title']
            self.update_progress(
                80 + int(20 * (index - 1) / len(matches)),
                title)
            items.extend(self.get_mapped_show_items(tmdb_id))
        self.update_progress(100, 'Complete')
        return items

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    def get_cached_items(self):
        # Day freshness and item-detail factories own caching, including empty results.
        return self.get_uncached_items()

    def get_uncached_items(self):
        self.dialog_progress_bg = DialogProgressSyncBG()
        self.dialog_progress_bg.heading = self.plugin_category
        self.dialog_progress_bg.create()
        try:
            return self.get_library_calendar_items()
        finally:
            self.dialog_progress_bg.close()

    def get_library_calendar_items(self):
        self.update_progress(0, 'Checking library shows')
        if not self.library_ids:
            return []
        candidates = {item['id'] for item in self.get_calendar_items()}
        self.update_progress(80, 'Matching calendar shows to library')
        matches = sorted(candidates & (self.library_ids - self.dropped_ids))
        return self.get_library_episode_items(matches)

    @cached_property
    def calendar_items(self):
        return self.get_calendar_items_sorted()

    def get_calendar_items_sorted(self):
        items = sorted(self.filtered_items, key=lambda item: (
            item['infolabels']['premiered'], item['unique_ids']['tvshow.tmdb'],
            item['infolabels']['season'], item['infolabels']['episode']))
        if get_setting('calendar_flatten'):
            items = LibraryCalendarItemStacker(items).items
        return items[::-1] if self.startdate < -1 else items

    @cached_property
    def count(self):
        return len(self.calendar_items)

    @cached_property
    def sorted_items(self):
        return self.calendar_items[self.item_a:self.item_z]


class ListLibraryCalendar(ListDefault):
    list_properties_class = ListLibraryCalendarProperties

    @cached_property
    def kodi_db(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('tv')

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.kodi_db = self.kodi_db
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(self, startdate, days, page=1, length=None, **kwargs):
        self.list_properties.tmdb_type = 'tv'
        self.list_properties.startdate = try_int(startdate)
        self.list_properties.days = try_int(days)
        self.list_properties.page = try_int(page) or 1
        self.list_properties.length = try_int(length)
        return self.get_items_finalised()
