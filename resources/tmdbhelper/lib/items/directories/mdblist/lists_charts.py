from tmdbhelper.lib.items.directories.lists_default import ListProperties, ListDefault
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import ListMDbListLocalProperties
from tmdbhelper.lib.items.directories.lists_local import UncachedListLocalData
from tmdbhelper.lib.items.directories.mapper_standard import FactoryItemMapper
from tmdbhelper.lib.items.directories.mdblist.mapper_charts import StreamingChartsItemMapper
from tmdbhelper.lib.addon.plugin import convert_type
from jurialmunkey.parser import try_int
from jurialmunkey.ftools import cached_property


class ListMDbListStreamingChartProperties(ListMDbListLocalProperties):

    rank = 1
    item_mapper_class = staticmethod(FactoryItemMapper)

    @cached_property
    def trakt_type(self):
        return convert_type(self.tmdb_type, 'trakt')

    @cached_property
    def cache_name_tuple(self):
        return (self.class_name, self.tmdb_type, self.rank, self.page, self.pmax)

    @cached_property
    def url(self):
        return self.request_url.format(trakt_type=self.trakt_type)

    @cached_property
    def response_kwgs(self):
        return {'rank': self.rank}

    @cached_property
    def container_content(self):
        return convert_type(self.tmdb_type, 'container')

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response(self.url, **self.response_kwgs)
        results = [i for i in response.json()['results'] if i['matched']]
        return UncachedListLocalData(results, self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties, trakt_type=self.trakt_type).item


class ListMDbListStreamingChart(ListStandard):

    list_properties_class = ListMDbListStreamingChartProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32545
        list_properties.request_url = 'justwatch/streaming-charts/{trakt_type}'
        list_properties.mdblist_api = self.mdblist_api
        return list_properties

    def get_items(self, *args, rank=1, **kwargs):
        rank = try_int(rank)
        self.list_properties.rank = rank if rank in (1, 7, 30) else 1
        return super().get_items(*args, **kwargs)


class ListMDbListStreamingChartsProperties(ListProperties):

    container_content = ''
    item_mapper_class = StreamingChartsItemMapper
    ranks = (
        (1, 33006),
        (7, 32284),
        (30, 32326),
    )

    @cached_property
    def items(self):
        return [
            self.get_mapped_item({'tmdb_type': self.tmdb_type, 'rank': rank, 'localize': localize})
            for rank, localize in self.ranks
        ]

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item


class ListMDbListStreamingCharts(ListDefault):

    list_properties_class = ListMDbListStreamingChartsProperties
    kodi_db = None

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32545
        list_properties.pagination = False
        return list_properties
