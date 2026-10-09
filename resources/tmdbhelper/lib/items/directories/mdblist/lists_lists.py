from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.items.directories.mdblist.lists_local import ListMDbListLocalNoCacheProperties
from tmdbhelper.lib.items.directories.lists_local import UncachedListLocalData
from tmdbhelper.lib.items.directories.mdblist.mapper_lists import ListsMDbListItemMapper, OfficialListsMDbListItemMapper
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, convert_type


class ListMDbListListsProperties(ListMDbListLocalNoCacheProperties):
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
        return UncachedListLocalData(response.json(), self.page, self.limit).data

    def get_mapped_item(self, item, add_infoproperties=None):
        return ListsMDbListItemMapper(item, add_infoproperties).item


class ListMDbListListsLikedProperties(ListMDbListListsProperties):

    limit = 100

    def get_api_response(self, page=1):
        response = self.mdblist_api.get_response_json(self.url, limit=self.limit, offset=(self.page - 1) * self.limit)
        try:
            total = int(response['pagination']['total'])
        except (KeyError, TypeError, ValueError):
            total = 0
        return {
            'json': response.get('lists') or [],
            'headers': {
                'x-pagination-page-count': (total + self.limit - 1) // self.limit,
                'x-pagination-item-count': total,
            }
        }


class ListMDbListListsOfficialProperties(ListMDbListListsProperties):
    @cached_property
    def response_kwgs(self):
        return {'mediatype': convert_type(self.tmdb_type, 'trakt')}

    def get_mapped_item(self, item, add_infoproperties=None):
        mapper = OfficialListsMDbListItemMapper(item, add_infoproperties)
        mapper.list_tmdb_type = self.tmdb_type
        return mapper.item


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


class ListMDbListListsLiked(ListMDbListListsTop):

    list_properties_class = ListMDbListListsLikedProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Liked Lists'
        list_properties.request_url = 'lists/liked'
        return list_properties


class ListMDbListListsCurated(ListMDbListListsTop):

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Curated Lists'
        list_properties.request_url = 'lists/curated'
        return list_properties


class ListMDbListListsOfficial(ListMDbListListsTop):

    list_properties_class = ListMDbListListsOfficialProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.plugin_name = 'Official Lists'
        list_properties.request_url = 'lists/official'
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
