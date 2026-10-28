from tmdbhelper.lib.items.directories.sync.lists_standard import ListHistory, ListProviderSyncProperties
from tmdbhelper.lib.sync.watchedon import ItemListSyncDataWatchedOn, WatchedOnDateParts


class ListWatchedOnProperties(ListProviderSyncProperties):

    def get_sync_data(self):
        if not self.provider_available:
            return
        sync_data = ItemListSyncDataWatchedOn(
            sort_by=self.sort_by,
            sort_how=self.sort_how,
            item_type=self.item_type,
            item_keys=self.item_keys,
            tmdb_id=self.tmdb_id)
        sync_data.watched_on = self.watched_on
        sync_data.sort = {**sync_data.sort, **self.sync_sort}
        return sync_data.items


class ListWatchedOn(ListHistory):

    list_properties_class = ListWatchedOnProperties

    def get_items(self, tmdb_type, day=None, month=None, year=None, **kwargs):
        self.list_properties.watched_on = WatchedOnDateParts(day=day, month=month, year=year)
        return super().get_items(tmdb_type=tmdb_type, **kwargs)
