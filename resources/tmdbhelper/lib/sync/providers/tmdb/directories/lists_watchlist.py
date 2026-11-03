from tmdbhelper.lib.items.directories.lists_default import ListSliceProperties
from tmdbhelper.lib.sync.providers.tmdb.directories.lists_authenticated import (
    ListAuthenticatedNoCache, ListAuthenticatedNoCacheProperties,
)


class ListWatchlistCombinedProperties(ListSliceProperties, ListAuthenticatedNoCacheProperties):
    def get_watchlist_items(self, tmdb_type):
        items = self.provider.user_lists.get_account_items(tmdb_type, 'watchlist')
        if items is None:
            return
        return [dict(item, media_type=tmdb_type) for item in items]

    def get_uncached_items(self):
        if not self.provider.is_user_authorized:
            return []
        movies = self.get_watchlist_items('movie')
        shows = self.get_watchlist_items('tv')
        if movies is None or shows is None:
            return []
        return [self.get_mapped_item(item) for item in movies + shows]


class ListWatchlist(ListAuthenticatedNoCache):
    @property
    def list_properties_class(self):
        if self.params.get('tmdb_type') in ('movie', 'tv'):
            return ListAuthenticatedNoCacheProperties
        return ListWatchlistCombinedProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'account/{{account_id}}/{tmdb_type}/watchlist'
        list_properties.request_kwgs = {'sort_by': 'created_at.desc'}
        list_properties.localize = 32193
        return list_properties
