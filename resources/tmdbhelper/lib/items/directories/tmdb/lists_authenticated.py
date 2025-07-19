from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.api.tmdb.users import TMDbUser
from jurialmunkey.ftools import cached_property


class ListAuthenticatedProperties(ListStandardProperties):

    request_kwgs = {}

    @cached_property
    def url(self):
        url = self.request_url.format(tmdb_type=self.tmdb_type)
        url = self.tmdb_user_api.format_authorised_path(url)
        return url

    def get_api_response(self, page=1):
        return self.tmdb_user_api.get_authorised_response_json(self.url, page=page, **self.request_kwgs)


class ListAuthenticatedNoCacheProperties(ListAuthenticatedProperties):
    def get_cached_items(self, *args, **kwargs):
        return self.get_uncached_items(*args, **kwargs)


class ListAuthenticatedNoCacheListListsProperties(ListAuthenticatedNoCacheProperties):
    def get_mapped_item(self, item, add_infoproperties=None):
        list_id = str(item.get('id') or '')
        user_id = self.tmdb_user_api.authenticator.authorised_access.get('account_id')

        return {
            'label': item.get('name') or '',
            'infolabels': {
                'plot': item.get('description'),
            },
            'infoproperties': {
                k: v for k, v in item.items()
                if v and type(v) not in [list, dict]
            },
            'art': {
                'icon': self.tmdb_imagepath.get_imagepath_fanart(item.get('backdrop_path')),
                'fanart': self.tmdb_imagepath.get_imagepath_fanart(item.get('backdrop_path')),
            },
            'params': {
                'info': 'tmdb_v4_list',
                'tmdb_type': 'both',
                'list_name': item.get('name') or '',
                'list_id': list_id,
                'user_id': user_id,
                'plugin_category': item.get('name') or '',
            },
            'unique_ids': {
                'list': list_id,
                'user': user_id,
            },
            'context_menu': []
        }


class ListAuthenticated(ListStandard):
    default_cacheonly = False
    list_properties_class = ListAuthenticatedProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.dbid_sorted = True
        list_properties.tmdb_user_api = TMDbUser()
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


class ListWatchlist(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/watchlist'
        list_properties.request_kwgs = {'sort_by': 'created_at.desc'}
        list_properties.localize = 32193
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
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/lists'
        list_properties.localize = 32211
        return list_properties
