from tmdbhelper.lib.items.directories.sync.lists_standard import ListStandardSync, ListSyncProperties


class ListFavoritesProperties(ListSyncProperties):
    def get_sync_data(self):
        if not self.trakt_api.authenticator.is_authorized:
            return
        return super().get_sync_data()


class ListFavorites(ListStandardSync):
    list_properties_class = ListFavoritesProperties

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.trakt_api = self.trakt_api
        list_properties.sync_type = 'favorites'
        list_properties.sort_by = 'unsorted'
        list_properties.localize = 1036
        return list_properties
