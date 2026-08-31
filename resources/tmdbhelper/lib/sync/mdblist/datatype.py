from tmdbhelper.lib.addon.consts import MDBLIST_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodesInShows
# from tmdbhelper.lib.addon.logger import kodi_log


class MDbListDataType(DataType):

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

    @staticmethod
    def get_next_cursor(response):
        try:
            if not response.headers['x-has-more']:
                return
            return response.headers['x-next-cursor']
        except KeyError:
            return

    def get_data_list_by_type(self, data):
        try:
            return data[f'{self.item_type}s']
        except KeyError:
            pass

    def get_response_sync_list(self, *args, **kwargs):
        response = self.get_response_sync_data(*args, **kwargs)

        # Check we actually get a response
        if response is None:
            return

        try:
            data = response.json()
            data = self.get_data_list_by_type(data)
        except AttributeError:
            return

        if not isinstance(data, list):
            return

        # Check if we have a next_cursor and if we need the data
        next_cursor = self.get_next_cursor(response)

        if next_cursor:  # and self.is_next_required(data):
            self.dialog_progress_bg.update(
                self.dialog_progress_bg.increment(),
                message='Retrieving next_cursor'
            )
            kwargs['cursor'] = next_cursor
            data.extend(self.get_response_sync_list(*args, **kwargs) or [])

        return data

    def get_response_sync(self, *args, **kwargs):
        return self.get_response_sync_list(*args, **kwargs)


class MDbListDataTypeEpisodesInShows(DataTypeEpisodesInShows, MDbListDataType):
    pass


class MDbListDataTypeEpisodesToShows(MDbListDataTypeEpisodesInShows):
    @property
    def syncitem_class(self):
        from tmdbhelper.lib.sync.mdblist.itemdata import MDbListSyncItemEpisodesToShows
        return MDbListSyncItemEpisodesToShows


class MDbListDataTypeNull(MDbListDataType):  # NullType for when no corresponding MDbList data for sync

    keys = tuple()

    def get_response_sync(self, *args, **kwargs):
        return []
