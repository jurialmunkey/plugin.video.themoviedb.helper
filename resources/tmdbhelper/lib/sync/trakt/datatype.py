from tmdbhelper.lib.addon.consts import TRAKT_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.sync.datatype import DataType, DataTypeEpisodes


class TraktDataType(DataType):

    @property
    def sync_args(self):
        return ('sync', self.method, f'{self.item_type}s',)

    def get_syncitem(self, meta):
        from tmdbhelper.lib.sync.trakt.itemdata import TraktSyncItem
        return TraktSyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

    def get_response_sync_data(self, *args, **kwargs):
        kwargs['limit'] = TRAKT_MAX_ITEMS_PER_PAGE
        path = self.trakt_api.get_request_url(*args, **kwargs)
        data = self.trakt_api.get_api_request(path, headers=self.trakt_api.headers)
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

        # Dumb hack to deal with weird Trakt decision to paginate sync endpoints without
        # Unclear why trakt would do this when unable to determine how deep to go from last activity
        # TODO: future method could check if sorting by activity then check item stamps to test depth?
        try:
            page_count = int(response.headers['x-pagination-page-count']) + 1
            page_start = int(response.headers['x-pagination-page']) + 1
        except (KeyError, ValueError):
            page_count = 0
            page_start = 0

        def get_next_item(x):
            # TODO: Might need some better validation here to check for timeouts autherror etc.
            try:
                return self.get_response_sync_data(*args, **kwargs, page=x).json()
            except (TypeError, ValueError, AttributeError):
                return

        with ParallelThread(range(page_start, page_count), get_next_item) as pt:
            next_data = pt.queue

        for i in next_data:
            if i is None:
                continue
            this_data.extend(i)

        return this_data


class TraktDataTypeEpisodes(DataTypeEpisodes, TraktDataType):
    pass
