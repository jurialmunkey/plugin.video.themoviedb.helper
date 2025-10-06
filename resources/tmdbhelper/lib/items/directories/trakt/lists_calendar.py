from jurialmunkey.parser import boolean, try_int
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta, get_calendar_name, datetime_in_range
from tmdbhelper.lib.items.directories.trakt.lists_standard import ListTraktStandardProperties
from tmdbhelper.lib.items.directories.trakt.lists_filtered import ListTraktFiltered
from tmdbhelper.lib.items.directories.trakt.mapper_calendar import (
    FactoryCalendarEpisodeItemMapper,
    FactoryCalendarMovieItemMapper,
)
from tmdbhelper.lib.items.directories.mdblist.lists_local import (
    UncachedMDbListItemsPage,
    UncachedMDbListLocalData,
)
from tmdbhelper.lib.items.directories.lists_default import ItemCache


class CalendarItemCollect:

    def __init__(self):
        self.items = []

    def append(self, item):
        self.items.append(item)

    @staticmethod
    def get_formatted_label(item):
        return f"{item['infolabels']['season']}x{item['infolabels']['episode']:02}"

    @cached_property
    def tmdb_id(self):
        return self.items[0]['unique_ids']['tvshow.tmdb']

    @cached_property
    def stacked_count(self):
        return f'{len(self.items)}'

    @cached_property
    def stacked_episodes(self):
        return ', '.join(self.stacked_episodes_list)

    @cached_property
    def stacked_episodes_list(self):
        return [
            self.get_formatted_label(i)
            for i in self.items
        ]

    @cached_property
    def stacked_episodes_with_titles_list(self):
        return [
            f'{self.get_formatted_label(i)} - {i["label"]}'
            for i in self.items
        ]

    @cached_property
    def infoproperties(self):
        return {
            'stacked_count': self.stacked_count,
            'stacked_episodes': self.stacked_episodes,
            'stacked_labels': ', '.join(self.stacked_episodes_with_titles_list),
            'stacked_titles': ', '.join([i['label'] for i in self.items]),
            'stacked_first': self.stacked_episodes_list[0],
            'stacked_last': self.stacked_episodes_list[-1],
            'stacked_first_episode': self.items[0]['infolabels']['episode'],
            'stacked_last_episode': self.items[-1]['infolabels']['episode'],
            'stacked_first_season': self.items[0]['infolabels']['season'],
            'stacked_last_season': self.items[-1]['infolabels']['season'],
            'stacked_first_title': self.items[0]['label'],
            'stacked_last_title': self.items[-1]['label'],
            'label_affix': f"{self.stacked_episodes_list[0]} - {self.stacked_episodes_list[-1]}",
            'label_override': self.label
        }

    @cached_property
    def params(self):
        return {
            'info': 'specified_episodes',
            'tmdb_id': self.tmdb_id,
            'tmdb_type': 'tv',
            'episodes': '/'.join(self.stacked_episodes_list),
        }

    @cached_property
    def infolabels(self):
        return {
            'title': self.label,
            'mediatype': 'tvshow',
        }

    @cached_property
    def label(self):
        return self.items[0]['infolabels']['tvshowtitle']

    @cached_property
    def item(self):
        if not self.items:
            return {}

        if len(self.items) == 1:
            return self.items[0]

        return {
            'params': self.params,
            'label': self.label,
            'infolabels': self.infolabels,
            'infoproperties': self.infoproperties,
            'unique_ids': self.items[0]['unique_ids'],
        }


class CalendarItemStacker:

    prev_item_id = None
    next_item_id = None

    def __init__(self, source_items):
        self.source_items = source_items

    def get_item_id(self, item):
        try:
            item_id = (
                item['unique_ids']['tvshow.slug'],
                item['infolabels']['premiered'],
            )
            return f'{item_id}'
        except (KeyError, TypeError):
            return

    @cached_property
    def items(self):
        items = []

        for i in self.source_items:

            if not items or self.get_item_id(items[-1].items[0]) != self.get_item_id(i):
                items.append(CalendarItemCollect())

            items[-1].append(i)

        return [i.item for i in items]


class ListTraktMyAiring(ListTraktFiltered):
    """
    For tv/movie type calendars
    """

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'calendars/my/{trakt_type}s'
        list_properties.plugin_name = f'{get_localized(32201)} {{plural}} {{localized}}'
        list_properties.localize = 32202
        list_properties.sub_type = True
        return list_properties


class CachedResponse:
    def __init__(self, trakt_api, url, trakt_filters):
        self.trakt_filters = trakt_filters
        self.trakt_api = trakt_api
        self.url = url

    cache_days = 0.25

    @cached_property
    def cache_name(self):
        cache_name_list = [f'{k}={v}' for k, v in self.trakt_filters.items()]
        cache_name_list = sorted(cache_name_list)
        cache_name_list = ['TraktData', self.url] + cache_name_list
        return '_'.join(cache_name_list)

    @ItemCache('ItemContainer.db')
    def get_cached_response(self):
        data = self.trakt_api.get_response(self.url, **self.trakt_filters)
        return data.json() if data else None

    @cached_property
    def json(self):
        return self.get_cached_response()


class ListTraktCalendarProperties(ListTraktStandardProperties):
    """
    For episode type calendars
    """

    class_pages = UncachedMDbListItemsPage
    trakt_path = ''
    trakt_user = 'my'
    trakt_authorization = True
    request_url = 'calendars/{trakt_user}/shows/{trakt_path}{start_date}/{total_days}'

    def get_cache_name_list_prefix(self):
        return [
            self.class_name,
            self.trakt_user,
            self.trakt_date,
            self.trakt_days,
            self.trakt_path,
        ]

    @cached_property
    def url(self):
        return self.request_url.format(
            trakt_user=self.trakt_user,
            start_date=self.start_date,
            total_days=self.total_days,
            trakt_path=self.trakt_path,
        )

    @cached_property
    def start_date(self):
        start_date = self.trakt_date - 1
        start_date = get_datetime_today() + get_timedelta(days=start_date)
        start_date = start_date.strftime('%Y-%m-%d')
        return start_date

    @cached_property
    def total_days(self):
        total_days = self.trakt_days + 2
        return total_days

    @cached_property
    def plugin_category(self):
        plugin_category = get_calendar_name(startdate=self.trakt_date, days=self.trakt_days)
        plugin_category = f'{plugin_category} ({self.trakt_path[:-1].capitalize()})' if self.trakt_path else plugin_category
        return plugin_category

    @cached_property
    def sorted_items(self):
        """
        Reverse items if starting in the past so that most recent are first
        """
        from tmdbhelper.lib.addon.plugin import get_setting
        return self.get_stacked_items() if get_setting('calendar_flatten') else self.get_unstacked_items()

    def get_unstacked_items(self):
        return self.filtered_items[::-1] if self.trakt_date < -1 else self.filtered_items

    def get_stacked_items(self):
        sorted_items = CalendarItemStacker(self.filtered_items).items
        return sorted_items[::-1] if self.trakt_date < -1 else sorted_items

    @cached_property
    def api_response_json(self):
        return self.get_api_response_json()

    def get_api_response_json(self):
        if self.trakt_authorization and not self.trakt_api.is_authorized:
            return
        return CachedResponse(self.trakt_api, self.url, self.trakt_filters).json

    def get_api_response(self, page=1):
        if not self.api_response_json:
            return
        return UncachedMDbListLocalData(self.api_response_json, self.page, self.limit).data

    def get_mapped_item_air_date_check(self, item_mapper):
        if not item_mapper.air_date:
            return
        if not datetime_in_range(item_mapper.air_date, days=self.trakt_days, start_date=self.trakt_date):
            return
        return item_mapper.item

    def get_mapped_item(self, item, add_infoproperties=None):
        item_mapper = FactoryCalendarEpisodeItemMapper(item, add_infoproperties)
        return self.get_mapped_item_air_date_check(item_mapper)


class ListTraktCalendarMovieProperties(ListTraktCalendarProperties):
    def get_mapped_item(self, item, add_infoproperties=None):
        item_mapper = FactoryCalendarMovieItemMapper(item, add_infoproperties)
        return self.get_mapped_item_air_date_check(item_mapper)


class ListLocalCalendarProperties(ListTraktCalendarProperties):

    @cached_property
    def kodi_db(self):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library('tv')

    def is_kodi_dbid(self, i):
        if not self.kodi_db:
            return False

        try:
            uids = i['show']['ids']
        except KeyError:
            return False

        if not self.kodi_db.get_info(
            info='dbid',
            tmdb_id=uids.get('tmdb'),
            tvdb_id=uids.get('tvdb'),
            imdb_id=uids.get('imdb')
        ):
            return False

        return True

    @cached_property
    def api_response_json(self):
        api_response_json = self.get_api_response_json() or []
        api_response_json = [i for i in api_response_json if self.is_kodi_dbid(i)]
        return api_response_json

    def get_api_response(self, page=1):
        if not self.api_response_json:
            return
        return UncachedMDbListLocalData(self.api_response_json, self.page, self.limit).data


class ListTraktCalendar(ListTraktFiltered):
    list_properties_class = ListTraktCalendarProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'calendars/{trakt_user}/shows/{trakt_path}{start_date}/{total_days}'
        list_properties.container_content = 'episodes'
        list_properties.trakt_type = 'episode'
        return list_properties

    def get_items(self, *args, startdate, days, endpoint=None, user=True, tmdb_type='tv', **kwargs):
        self.list_properties.trakt_user = 'my' if boolean(user) else 'all'
        self.list_properties.trakt_date = try_int(startdate)
        self.list_properties.trakt_days = try_int(days)
        self.list_properties.trakt_path = f'{endpoint}/' if endpoint else ''
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)


class ListTraktMoviesCalendar(ListTraktFiltered):

    list_properties_class = ListTraktCalendarMovieProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_authorization = True
        list_properties.request_url = 'calendars/{trakt_user}/movies/{start_date}/{total_days}'
        list_properties.container_content = 'movies'
        list_properties.trakt_type = 'movie'
        return list_properties

    def get_items(self, *args, startdate, days, user=True, tmdb_type='movie', **kwargs):
        self.list_properties.trakt_user = 'my' if boolean(user) else 'all'
        self.list_properties.trakt_date = try_int(startdate)
        self.list_properties.trakt_days = try_int(days)
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)


class ListTraktDVDsCalendar(ListTraktMoviesCalendar):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'calendars/{trakt_user}/dvd/{start_date}/{total_days}'
        return list_properties


class ListLocalCalendar(ListTraktCalendar):
    list_properties_class = ListLocalCalendarProperties

    def get_items(self, *args, user=True, **kwargs):  # Absorb user param
        return super().get_items(*args, user=False, **kwargs)  # Force user to be False since we need to check library against all items
