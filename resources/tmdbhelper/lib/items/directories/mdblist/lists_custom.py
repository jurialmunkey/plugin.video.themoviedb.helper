from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import ListMDbListLocalProperties
from tmdbhelper.lib.items.directories.lists_local import UncachedListLocalData
from tmdbhelper.lib.items.directories.trakt.mapper_standard import FactoryItemMapper
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.api.mapping import get_empty_item
from tmdbhelper.lib.addon.plugin import get_setting, get_localized, convert_type, ADDONPATH
from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property


class UncachedMDbListCustomData(UncachedListLocalData):
    @cached_property
    def headers(self):
        return self.response.headers

    @cached_property
    def item_count(self):
        return int(self.headers['X-Total-Items'])

    @cached_property
    def json(self):
        return self.response.json() or {}

    @cached_property
    def data(self):
        return {
            'json': self.json,
            'headers': {
                'x-pagination-page-count': self.page_count,
                'x-pagination-item-count': self.item_count,
            }
        } if self.response else {}


class ListMDbListCustomProperties(ListMDbListLocalProperties):

    genre = None
    sort_by = None
    sort_how = None

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = [
            self.class_name,
            self.list_id,
            self.tmdb_type
        ] + sorted([
            f'{k}={v}' for k, v in self.response_kwgs.items()
        ])
        return tuple(cache_name_tuple)

    @cached_property
    def url(self):
        return self.request_url.format(list_id=self.list_id)

    @cached_property
    def offset(self):
        return ((self.page - 1) * 20)

    @cached_property
    def response_kwgs(self):
        return {
            k: v for k, v in (
                ('sort', self.sort_by),
                ('order', self.sort_how),
                ('limit', self.limit),
                ('offset', self.offset),
                ('filter_genre', self.genre),
                ('unified', 'true'),
            ) if v
        }

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response(self.url, **self.response_kwgs)
        return UncachedMDbListCustomData(response, self.page, self.limit).data


class ListMDbListCustom(ListStandard):

    list_properties_class = ListMDbListCustomProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'TMDbHelper'
        list_properties.request_url = 'lists/{list_id}/items'
        list_properties.mdblist_api = self.mdblist_api
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        return list_properties

    def get_items(
        self,
        *args,
        list_id,
        genre=None,
        tmdb_type=None,
        sort_by=None,
        sort_how=None,
        **kwargs
    ):
        self.list_properties.list_id = list_id
        self.list_properties.genre = genre
        self.list_properties.tmdb_type = tmdb_type or 'both'
        self.list_properties.sort_by = sort_by
        self.list_properties.sort_how = sort_how
        return super().get_items(*args, tmdb_type=tmdb_type or 'both', **kwargs)


class ListMDbListOfficialProperties(ListMDbListCustomProperties):
    @cached_property
    def response_kwgs(self):
        response_kwgs = super().response_kwgs
        response_kwgs['mediatype'] = convert_type(self.tmdb_type, 'trakt')
        return response_kwgs

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container', items=self.items)


class ListMDbListOfficial(ListMDbListCustom):

    list_properties_class = ListMDbListOfficialProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'lists/official/{list_id}/items'
        return list_properties


class ListMDbListStreamingChartsProperties(ListMDbListLocalProperties):

    period = 1

    @cached_property
    def cache_name_tuple(self):
        return (self.class_name, self.tmdb_type, self.period, self.page, self.pmax)

    @cached_property
    def url(self):
        return self.request_url.format(mediatype=convert_type(self.tmdb_type, 'trakt'))

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container')

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response_json(self.url, period=self.period)
        results = [i for i in response.get('results') or [] if (i.get('ids') or {}).get('tmdb')]
        return UncachedListLocalData(results, self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return FactoryItemMapper(item, add_infoproperties, trakt_type=item.get('mediatype')).item


class ListMDbListStreamingCharts(ListStandard):

    list_properties_class = ListMDbListStreamingChartsProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32543
        list_properties.request_url = 'justwatch/streaming-charts/{mediatype}'
        list_properties.mdblist_api = self.mdblist_api
        return list_properties

    def get_items(self, *args, tmdb_type=None, period=1, **kwargs):
        if tmdb_type not in ('movie', 'tv'):
            return
        self.list_properties.period = try_int(period) or 1
        return super().get_items(*args, tmdb_type=tmdb_type, **kwargs)


class ListMDbListStreamingChartsPeriods(ContainerDirectory):
    periods = (
        (1, 33006),
        (7, 32284),
        (30, 32326),
    )

    def get_items(self, tmdb_type=None, **kwargs):
        if tmdb_type not in ('movie', 'tv'):
            return
        self.plugin_category = get_localized(32543)
        return [self.get_period_item(tmdb_type, period, localized) for period, localized in self.periods]

    @staticmethod
    def get_period_item(tmdb_type, period, localized):
        item = get_empty_item()
        item['label'] = get_localized(localized)
        item['art'] = {'icon': f'{ADDONPATH}/resources/icons/mdblist/mdblist.png'}
        item['params'] = {'info': 'mdblist_streamingcharts', 'tmdb_type': tmdb_type, 'period': period}
        return item
