from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.activity import SyncLastActivities


class SyncActionInvalidator:
    """Refresh only the selected provider's dependencies for one item action."""

    def __init__(self, syncdata, provider, dependencies):
        self.syncdata = syncdata
        self.provider = provider
        self.dependencies = dependencies

    @cached_property
    def sync_items(self):
        return self.get_sync_items()

    def get_sync_items(self):
        items = {}
        for sync_type, item_type in self.dependencies:
            item = self.syncdata.create_sync(sync_type, item_type)
            if item is None or item.provider.provider_id != self.provider.provider_id:
                continue
            # Factories can map several requested types to the same stored activity.
            items[(item.item_type, item.cache_method)] = item
        return tuple(items.values())

    def invalidate_sync_item(self, item):
        self.syncdata.invalidate_activity(f'{item.item_type}.{item.cache_method}')

    def run(self):
        SyncLastActivities(self.syncdata, self.provider).clear()
        for item in self.sync_items:
            self.invalidate_sync_item(item)
        for item in self.sync_items:
            item.sync(forced=True)
