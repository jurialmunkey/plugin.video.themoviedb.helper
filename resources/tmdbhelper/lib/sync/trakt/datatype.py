from jurialmunkey.parser import try_int
from tmdbhelper.lib.addon.consts import TRAKT_MAX_ITEMS_PER_PAGE
from tmdbhelper.lib.sync.datatype import DataType
from tmdbhelper.lib.sync.trakt.activity import TraktLastActivities
from tmdbhelper.lib.sync.trakt.itemdata import TraktSyncItem


class TraktDataType(DataType):
    def __init__(self, instance_syncdata, item_type):
        super().__init__(instance_syncdata, item_type, None)

    @property
    def trakt_api(self):
        return self.instance_syncdata.core_sync.api

    @property
    def cache_method(self):
        return f'trakt.{self.method}'

    @property
    def sync_args(self):
        return ('sync', self.method, f'{self.item_type}s')

    def get_last_activities(self):
        return TraktLastActivities(self.instance_syncdata)

    def get_syncitem(self, meta):
        return TraktSyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

    def get_response_sync(self, *args, **kwargs):
        items = []
        page = 1
        while True:
            response = self.trakt_api.get_response(*args, page=page, limit=TRAKT_MAX_ITEMS_PER_PAGE, **kwargs)
            if response is None or response.status_code != 200:
                return
            try:
                data = response.json()
            except ValueError:
                return
            items.extend(data)
            if page >= try_int(response.headers.get('x-pagination-page-count'), fallback=1):
                return items
            page += 1
