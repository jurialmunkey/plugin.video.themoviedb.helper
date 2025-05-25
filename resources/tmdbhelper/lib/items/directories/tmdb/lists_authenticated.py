from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard
from tmdbhelper.lib.api.tmdb.users import TMDbUser
from tmdbhelper.lib.files.ftools import cached_property


class ListAuthenticated(ListStandard):
    default_cacheonly = False

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.dbid_sorted = True
        return list_properties

    @cached_property
    def tmdb_user_api(self):
        return TMDbUser()

    def _get_cached_items_page(self, request_url, tmdb_type, page=1):
        request_url = self.tmdb_user_api.format_authorised_path(request_url)
        response = self.tmdb_user_api.get_authorised_response_json(request_url, page=page)
        return self.get_cached_items_page_configured(response, tmdb_type)


class ListAuthenticatedNoCache(ListAuthenticated):
    def get_cached_items_page(self, *args, **kwargs):
        """ Override default caching method to prevent caching """
        return self._get_cached_items_page(*args, **kwargs)

    def get_cached_items(self, *args, **kwargs):
        """ Override default caching method to prevent caching """
        return self._get_cached_items(*args, **kwargs)


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
        list_properties.localize = 1036
        return list_properties


class ListWatchlist(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/watchlist'
        list_properties.localize = 32193
        return list_properties


class ListRated(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/rated'
        list_properties.localize = 32521
        return list_properties


class ListList(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'list/{list_id}'
        list_properties.localize = 32211
        return list_properties

    def get_request_url(self, list_id, **kwargs):
        return self.list_properties.request_url.format(list_id=list_id)


class ListLists(ListAuthenticatedNoCache):
    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/lists'
        list_properties.localize = 32211
        return list_properties

    def get_mapped_item(self, item, tmdb_type, add_infoproperties=None):
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
