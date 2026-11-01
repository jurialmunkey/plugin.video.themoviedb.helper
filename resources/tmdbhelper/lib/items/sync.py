from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.auth import SyncProviderAuthorisation


class SyncPlayData(SyncProviderAuthorisation):
    """Watched provider access for containers. The item detail service refreshes synced play data."""

    def __init__(self):
        super().__init__('watched')

    def get_provider(self):
        return self.syncdata.registry.get_selected_provider(self.capability)

    @cached_property
    def syncdata(self):
        from tmdbhelper.lib.sync.datasync import SyncDataFactory
        return SyncDataFactory()
