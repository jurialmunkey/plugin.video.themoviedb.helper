from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import (
    ListMDbListLocalProperties,
    UncachedMDbListLocalData,
)
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.ftools import cached_property
from jurialmunkey.parser import try_int


PAGES_LENGTH = get_setting('pagemulti_trakt', 'int') or 1


class UncachedMDbListCustomData(UncachedMDbListLocalData):
    @cached_property
    def headers(self):
        return self.response.headers

    @cached_property
    def item_count(self):
        return int(self.headers['X-Total-Items'])

    @cached_property
    def json(self):
        json = self.response.json() or {}
        json = [i for _, medialist in json.items() for i in medialist]
        return json

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

    @cached_property
    def cache_name_tuple(self):
        return (
            self.class_name,
            self.list_id,
            self.tmdb_type,
            self.page,
            self.length,
        )

    @cached_property
    def url(self):
        return self.request_url.format(list_id=self.list_id)

    @cached_property
    def offset(self):
        return ((self.page - 1) * 20)

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response(self.url, limit=self.limit, offset=self.offset)
        return UncachedMDbListCustomData(response, self.page, self.limit).data


class ListMDbListCustom(ListStandard):

    list_properties_class = ListMDbListCustomProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'TMDbHelper'
        list_properties.request_url = 'lists/{list_id}/items'
        list_properties.mdblist_api = self.mdblist_api
        return list_properties

    def get_items(self, *args, list_id, length=None, tmdb_type=None, **kwargs):
        self.list_properties.list_id = list_id
        self.list_properties.tmdb_type = tmdb_type or 'both'
        return super().get_items(
            *args,
            length=try_int(length) or PAGES_LENGTH,
            tmdb_type=tmdb_type or 'both',
            **kwargs
        )
