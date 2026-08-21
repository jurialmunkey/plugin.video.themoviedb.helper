from tmdbhelper.lib.addon.consts import MDBLIST_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodesInShows, DataTypeEpisodesNotShows
from tmdbhelper.lib.addon.logger import kodi_log


class MDbListDataType(DataType):

    @property
    def data_key(self):
        return f'{self.item_type}s'

    @property
    def sync_args(self):
        return (self.method,)

    def get_syncitem(self, meta):
        from tmdbhelper.lib.sync.mdblist.itemdata import MDbListSyncItem
        return MDbListSyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

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
        if self.data_key is None:
            return data
        try:
            return data[self.data_key]
        except KeyError:
            pass

    def get_response_sync(self, *args, **kwargs):
        response = self.get_response_sync_data(*args, **kwargs)

        # Check we actually get a response
        if response is None:
            return

        try:
            data = response.json()
            data = self.get_data_list_by_type(data)
        except AttributeError:
            return

        if not data or not isinstance(data, list):
            return

        # Check if we have a next_cursor and if we need the data
        next_cursor = self.get_next_cursor(response)

        if next_cursor:  # and self.is_next_required(data):
            kodi_log(f'Sync: next_cursor: {args} {kwargs}', 2)
            kwargs['cursor'] = next_cursor
            data.extend(self.get_response_sync(*args, **kwargs) or [])
        else:
            kodi_log(f'Sync: stop_cursor: {args} {kwargs}', 2)

        return data


class MDbListDataTypeEpisodesInShows(DataTypeEpisodesInShows, MDbListDataType):
    pass


class MDbListDataTypeEpisodesNotShows(DataTypeEpisodesNotShows, MDbListDataType):
    pass
