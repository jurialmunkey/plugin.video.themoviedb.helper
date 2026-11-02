from jurialmunkey.ftools import cached_property


class ServiceActions:
    def __init__(self, registry=None, syncdata=None):
        self._registry = registry
        self._syncdata = syncdata

    @cached_property
    def registry(self):
        return self.get_registry()

    def get_registry(self):
        from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
        return self._registry if self._registry is not None else SyncProviderRegistry()

    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    def get_syncdata(self):
        from tmdbhelper.lib.sync.datasync import SyncData
        return self._syncdata if self._syncdata is not None else SyncData(self.registry)

    @cached_property
    def actions(self):
        return self.get_actions()

    def get_actions(self):
        return self.get_provider_actions()

    def get_provider_actions(self):
        return {
            name: (provider, action_class)
            for provider in self.registry.get_capable_providers('service_actions')
            if provider.is_authorized()
            for name, action_class in provider.service_action_classes.items()
        }

    def get_item(self, name, *args):
        provider, action_class = self.actions[name]
        item = action_class(*args)
        item.sync_provider = provider
        item.syncdata = self.syncdata
        return item
