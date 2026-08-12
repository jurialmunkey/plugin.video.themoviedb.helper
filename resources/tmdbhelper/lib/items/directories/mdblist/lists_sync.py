from datetime import date

from tmdbhelper.lib.items.directories.mdblist.lists_custom import (
    ListMDbListCustom,
    ListMDbListCustomProperties,
    UncachedMDbListCustomData,
)
from tmdbhelper.lib.items.directories.mdblist.mapper_upnext import MDbListUpNextItemMapper
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int


class ListMDbListWatchlistProperties(ListMDbListCustomProperties):

    released_from = None
    released_to = None

    @cached_property
    def url(self):
        return 'watchlist/items'

    @cached_property
    def response_kwgs(self):
        response_kwgs = super().response_kwgs
        response_kwgs.update({
            k: v for k, v in (
                ('mediatype', 'show' if self.tmdb_type == 'tv' else self.tmdb_type),
                ('released_from', self.released_from),
                ('released_to', self.released_to),
            ) if v
        })
        return response_kwgs


class ListMDbListWatchlist(ListMDbListCustom):

    list_properties_class = ListMDbListWatchlistProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32193
        list_properties.list_id = 'watchlist'
        return list_properties

    def get_items(
        self,
        tmdb_type,
        page=1,
        length=None,
        sort_by=None,
        sort_how=None,
        **kwargs
    ):
        self.list_properties.tmdb_type = tmdb_type
        self.list_properties.page = try_int(page) or 1
        self.list_properties.length = try_int(length)
        self.list_properties.sort_by = sort_by or self.list_properties.sort_by
        self.list_properties.sort_how = sort_how or self.list_properties.sort_how
        return self.get_items_finalised()


class ListMDbListWatchlistReleased(ListMDbListWatchlist):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32456
        list_properties.sort_by = 'released'
        list_properties.sort_how = 'desc'
        list_properties.released_to = date.today().isoformat()
        return list_properties


class ListMDbListWatchlistAnticipated(ListMDbListWatchlist):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32457
        list_properties.sort_by = 'released'
        list_properties.sort_how = 'asc'
        list_properties.released_from = date.today().isoformat()
        return list_properties


class UncachedMDbListUpNextData(UncachedMDbListCustomData):
    @cached_property
    def response_data(self):
        return self.response.json() or {}

    @cached_property
    def json(self):
        return self.response_data.get('items') or []

    @cached_property
    def item_count(self):
        return ((self.page - 1) * self.limit) + len(self.json)

    @cached_property
    def page_count(self):
        return self.page + 1 if self.response_data.get('has_more') else self.page


class ListMDbListNextEpisodesProperties(ListMDbListCustomProperties):

    @cached_property
    def limit(self):
        return min(super().limit, 100)

    @cached_property
    def cache_name_tuple(self):
        return (
            self.class_name,
            self.tmdb_type,
            self.page,
            self.limit,
        )

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response(
            'upnext',
            limit=self.limit,
            offset=((self.page - 1) * self.limit),
        )
        return UncachedMDbListUpNextData(response, self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return MDbListUpNextItemMapper(item, add_infoproperties).item


class ListMDbListNextEpisodes(ListStandard):

    list_properties_class = ListMDbListNextEpisodesProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = '{localized}'
        list_properties.localize = 32197
        list_properties.mdblist_api = self.mdblist_api
        list_properties.page_length = get_setting('pagemulti_trakt', 'int') or 1
        list_properties.tmdb_type = 'tv'
        list_properties.container_content = 'episodes'
        return list_properties

    def get_items(self, page=1, length=None, **kwargs):
        self.list_properties.page = try_int(page) or 1
        self.list_properties.length = try_int(length)
        return self.get_items_finalised()
