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

    def get_response_sync(self, *args, **kwargs):
        response = self.get_response_sync_data(*args, **kwargs)

        # Check we actually get a response
        if response is None:
            return
        try:
            this_data = response.json()
        except (ValueError, AttributeError):
            return

        # TODO: CURSOR DEPTH RETRIEVAL
        # try:
        #     next_cursor = response.headers['X-Next-Cursor']
        # except KeyError:
        #     next_cursor = None

        # def get_next_item(x):
        #     try:
        #         return self.get_response_sync_data(*args, **kwargs, cursor=next_cursor).json()
        #     except (TypeError, ValueError, AttributeError):
        #         return

        # for i in next_data:
        #     if i is None:
        #         continue
        #     this_data.extend(i)

        # Get the corresponding item_type list
        try:
            this_data = this_data[f'{self.item_type}s']
        except KeyError:
            return

        return this_data


class MDbListDataTypeEpisodes(DataTypeEpisodes, MDbListDataType):
    pass
