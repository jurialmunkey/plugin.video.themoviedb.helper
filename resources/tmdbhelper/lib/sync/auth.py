from jurialmunkey.ftools import cached_property


class SyncProviderAuthorisation:
    def __init__(self, capability):
        self.capability = capability

    @cached_property
    def provider(self):
        return self.get_provider()

    def get_provider(self):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return SyncProviderRegistry().get_selected_provider(self.capability)

    @property
    def authorisation_type(self):
        return self.provider.display_name if self.provider else ''

    @property
    def is_authorized(self):
        return self.provider is not None and self.provider.is_authorized()
