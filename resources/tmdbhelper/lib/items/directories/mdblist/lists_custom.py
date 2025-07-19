from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import (
    ListMDbListLocalProperties,
    UncachedMDbListLocalData,
)
from tmdbhelper.lib.addon.plugin import get_setting
from jurialmunkey.ftools import cached_property


class UncachedMDbListCustomData(UncachedMDbListLocalData):
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
