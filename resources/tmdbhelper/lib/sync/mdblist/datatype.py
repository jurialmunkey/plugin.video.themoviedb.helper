from tmdbhelper.lib.addon.consts import MDBLIST_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodes


class MDbListDataType(DataType):

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

    def get_response_sync(self, *args, **kwargs):
        response = self.get_response_sync_data(*args, **kwargs)

        # Check we actually get a response
        if response is None:
            return
        try:
            data = response.json()[f'{self.item_type}s']
        except (ValueError, AttributeError, KeyError):
            return

        # Check if we have a next_cursor and if we need the data
        next_cursor = self.get_next_cursor(response)

        from tmdbhelper.lib.addon.logger import kodi_log
        if next_cursor:  # and self.is_next_required(data):
            kodi_log('Sync: next_cursor required', 2)
            kwargs['cursor'] = next_cursor
            data.extend(self.get_response_sync(*args, **kwargs) or [])
        else:
            kodi_log('Sync: next_cursor not required', 2)

        return data


class MDbListDataTypeEpisodes(DataTypeEpisodes, MDbListDataType):
    pass
