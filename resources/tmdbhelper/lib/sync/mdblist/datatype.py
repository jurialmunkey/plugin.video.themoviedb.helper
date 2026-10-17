from tmdbhelper.lib.addon.consts import MDBLIST_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodesInShows
from tmdbhelper.lib.sync.mdblist.pagination import (
    MDbListSyncCollection,
    MDbListSyncCollectionSnapshot,
    MDbListSyncCollectionOffset,
)


class MDbListDataType(DataType):
    sync_collection_class = MDbListSyncCollection

    @property
    def sync_args(self):
        return (self.method,)

    @property
    def syncitem_class(self):
        from tmdbhelper.lib.sync.mdblist.itemdata import MDbListSyncItem
        return MDbListSyncItem

    def get_syncitem(self, meta):
        return self.syncitem_class(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

    def get_response_sync_data(self, *args, **kwargs):
        kwargs['limit'] = MDBLIST_MAX_ITEMS_PER_PAGE
        path = self.mdblist_api.get_request_url(*args, **kwargs)
        data = self.mdblist_api.get_api_request(path, headers=self.mdblist_api.headers)
        return data

    def get_data_list_by_type(self, data):
        try:
            return data[f'{self.item_type}s']
        except KeyError:
            pass

    def get_response_sync_list(self, *args, **kwargs):
        return self.sync_collection_class(self, *args, **kwargs).data

    def get_response_sync(self, *args, **kwargs):
        return self.get_response_sync_list(*args, **kwargs)


class MDbListDataTypeSnapshot(MDbListDataType):
    """ Require a complete paginated snapshot before replacing cached data. """

    sync_collection_class = MDbListSyncCollectionSnapshot


class MDbListDataTypeOffset(MDbListDataTypeSnapshot):
    sync_collection_class = MDbListSyncCollectionOffset


class MDbListDataTypeEpisodesInShows(DataTypeEpisodesInShows, MDbListDataType):
    pass


class MDbListDataTypeEpisodesToShows(MDbListDataTypeEpisodesInShows):
    @property
    def syncitem_class(self):
        from tmdbhelper.lib.sync.mdblist.itemdata import MDbListSyncItemEpisodesToShows
        return MDbListSyncItemEpisodesToShows


class MDbListDataTypeNull(MDbListDataType):  # NullType for when no corresponding MDbList data for sync

    keys = tuple()

    def clear_columns(self, keys):
        pass

    def get_response_sync(self, *args, **kwargs):
        return []
