from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.sync.lists_standard import ListHistory, ListProviderSyncProperties
from tmdbhelper.lib.items.directories.sync.mapper_watchedon import WatchedOnItemMapper
from tmdbhelper.lib.sync.watchedon import ItemListSyncDataWatchedOn, WatchedOnDateParts


class ListWatchedOnProperties(ListProviderSyncProperties):

    item_mapper_class = WatchedOnItemMapper

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

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        if not self.response:
            return
        return [self.get_mapped_item(item) for item in self.response.paginated_items.items]

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class({
            'entry': item,
            'watched_on': self.watched_on,
            'params_def': self.params_def,
        }, add_infoproperties).item


class ListWatchedOn(ListHistory):

    list_properties_class = ListWatchedOnProperties

    def get_items(self, tmdb_type, day=None, month=None, year=None, **kwargs):
        self.list_properties.watched_on = WatchedOnDateParts(day=day, month=month, year=year)
        return super().get_items(tmdb_type=tmdb_type, **kwargs)
