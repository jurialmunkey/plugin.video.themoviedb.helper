from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import (
    ListMDbListLocalProperties,
    UncachedMDbListLocalData,
)
from tmdbhelper.lib.items.directories.mdblist.mapper_lists import ListsMDbListItemMapper
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class ListMDbListListsProperties(ListMDbListLocalProperties):
    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = [
            self.class_name,
            self.page,
            self.pmax,
        ]
        cache_name_tuple += sorted([
            f'{k}={v}' for k, v in self.response_kwgs.items() if v
        ])
        return tuple(cache_name_tuple)

    @cached_property
    def url(self):
        return self.request_url

    response_kwgs = {}
    container_content = ''
    page_length = 12
    pmax = 12

    @cached_property
    def offset(self):
        return ((self.page - 1) * 20)

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response(self.url, **self.response_kwgs)
        return UncachedMDbListLocalData(response.json(), self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return ListsMDbListItemMapper(item, add_infoproperties).item


class ListMDbListListsTop(ListStandard):

    list_properties_class = ListMDbListListsProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Top Lists'
        list_properties.request_url = 'lists/top'
        list_properties.mdblist_api = self.mdblist_api
        return list_properties

    def get_items(self, *args, tmdb_type=None, **kwargs):
        return super().get_items(*args, tmdb_type=tmdb_type or 'both', **kwargs)


class ListMDbListListsUser(ListMDbListListsTop):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Your Lists'
        list_properties.request_url = 'lists/user'
        return list_properties


class ListMDbListListsSearch(ListMDbListListsTop):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Search Lists'
        list_properties.request_url = 'lists/search'
        return list_properties

    def get_items(self, *args, query=None, **kwargs):
        from xbmcgui import Dialog
        query = query or Dialog().input(get_localized(32044))
        self.list_properties.response_kwgs = {'query': query}
        return super().get_items(*args, **kwargs) if query else None
