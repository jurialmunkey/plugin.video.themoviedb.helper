from tmdbhelper.lib.sync.mdblist.datatype import MDbListDataType


class SyncWatchlist(MDbListDataType):
    keys = ('rank', 'listed_at', 'notes', )  # TODO: FIXME notes and rank?
    last_activities_key = 'watchlisted_at'
    method = 'watchlist/items'
    key_prefix = 'watchlist'

    @property
    def sync_kwgs(self):
        sync_kwgs = {'mediatype': self.item_type}
        return sync_kwgs


class SyncCollection(MDbListDataType):
    keys = ('last_collected_at', 'last_updated_at', )
    last_activities_key = 'collected_at'
    method = 'sync/collection'
    key_prefix = 'collection'

    @property
    def sync_kwgs(self):
        sync_kwgs = {'mediatype': self.item_type}
        return sync_kwgs
