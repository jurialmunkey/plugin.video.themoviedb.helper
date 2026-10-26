from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.lists_default import ListProperties


class SyncProviderListProperties(ListProperties):
    sync_capabilities = ('watched',)

    @cached_property
    def provider_available(self):
        return self.get_provider_available()

    def get_provider_available(self):
        from tmdbhelper.lib.script.sync.provider_setup import SyncProviderSetup
        return SyncProviderSetup(self.sync_capabilities).ensure_provider()
