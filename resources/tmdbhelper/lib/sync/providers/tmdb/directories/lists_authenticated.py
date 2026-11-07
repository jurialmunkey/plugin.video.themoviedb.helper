from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
from tmdbhelper.lib.sync.providers.tmdb.directories.mapper import TMDbUserListMapper
from tmdbhelper.lib.sync.providers.tmdb.directories.mapper_watchlist import TMDbWatchlistMapper
from jurialmunkey.ftools import cached_property


class ListAuthenticatedProperties(ListStandardProperties):

    request_kwgs = {}
    stale_hours = 0  # Account lists change when the user edits them, so always wait for new data

    @cached_property
    def url(self):
        url = self.request_url.format(tmdb_type=self.tmdb_type)
        url = self.provider.user_lists.format_path(url)
        return url

    def get_api_response(self, page=1):
        return self.provider.user_lists.get_response(self.url, page=page, **self.request_kwgs)

    def get_uncached_items(self):
        if not self.provider.is_user_authorized:
            return {'items': []}
        return super().get_uncached_items()


class ListAuthenticatedNoCacheProperties(ListAuthenticatedProperties):
    def get_cached_items(self, *args, **kwargs):
        return self.get_uncached_items(*args, **kwargs)


class ListAuthenticatedNoCacheListListsProperties(ListAuthenticatedNoCacheProperties):
    item_mapper_class = TMDbUserListMapper

    def get_uncached_items(self):
        if not self.provider.is_user_authorized:
            return {'items': []}
        items = super().get_uncached_items()
        if self.page == 1:
            items['items'].insert(0, self.get_watchlist_item())
        items['count'] += 1
        items['pages'] = max(items['pages'], 1)
        return items

    def get_watchlist_item(self):
        return TMDbWatchlistMapper({}, None).item

    def get_mapped_item(self, item, add_infoproperties=None):
        mapper = self.item_mapper_class(item, add_infoproperties)
        mapper.tmdb_imagepath = self.tmdb_imagepath
        mapper.user_id = self.provider.user_api.authenticator.stored_authorisation['account_id']
        return mapper.item


class ListAuthenticated(ListStandard):
    default_cacheonly = False
    list_properties_class = ListAuthenticatedNoCacheProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.dbid_sorted = True
        list_properties.provider = SyncProviderRegistry().get_provider('tmdb')
        list_properties.tmdb_api = list_properties.provider.api
        list_properties.tmdb_imagepath = self.tmdb_imagepath
        return list_properties


class ListAuthenticatedNoCache(ListAuthenticated):
    list_properties_class = ListAuthenticatedNoCacheProperties


class ListAuthenticatedNoCacheListLists(ListAuthenticated):
    list_properties_class = ListAuthenticatedNoCacheListListsProperties


class ListRecommendations(ListAuthenticated):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/recommendations'
        list_properties.localize = 32223
        return list_properties


class ListFavourites(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/favorites'
        list_properties.request_kwgs = {'sort_by': 'created_at.desc'}
        list_properties.localize = 1036
        return list_properties


class ListRated(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/rated'
        list_properties.request_kwgs = {'sort_by': 'created_at.desc'}
        list_properties.localize = 32521
        return list_properties


class ListList(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.localize = 32211
        return list_properties

    def get_items(self, *args, list_id=None, **kwargs):
        self.list_properties.request_url = f'list/{list_id}'
        return super().get_items(*args, **kwargs)


class ListLists(ListAuthenticatedNoCacheListLists):
    kodi_details = False

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/lists'
        list_properties.localize = 32211
        return list_properties
