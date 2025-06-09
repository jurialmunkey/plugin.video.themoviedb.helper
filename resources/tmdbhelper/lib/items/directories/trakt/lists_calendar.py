from jurialmunkey.parser import boolean, try_int
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta, get_calendar_name
from tmdbhelper.lib.items.directories.trakt.lists_standard import ListTraktStandardProperties
from tmdbhelper.lib.items.directories.trakt.lists_filtered import ListTraktFiltered
from tmdbhelper.lib.items.directories.trakt.mapper_calendar import FactoryCalendarEpisodeItemMapper
from tmdbhelper.lib.items.directories.mdblist.lists_local import UncachedMDbListItemsPage, UncachedMDbListLocalData
from tmdbhelper.lib.items.directories.lists_default import ItemCache


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
        return self.filtered_items[::-1] if self.trakt_date < -1 else self.filtered_items

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

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryCalendarEpisodeItemMapper(item, add_infoproperties).item


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


class ListLocalCalendar(ListTraktCalendar):
    list_properties_class = ListLocalCalendarProperties

    def get_items(self, *args, user=True, **kwargs):  # Absorb user param
        return super().get_items(*args, user=False, **kwargs)  # Force user to be False since we need to check library against all items
