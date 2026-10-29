from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.contains import CommonContainerAPIs


class ServiceActions(CommonContainerAPIs):
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
        actions = {}
        if self.trakt_api.authenticator.is_authorized:
            actions.update(self.get_trakt_actions())
        provider_actions = self.get_provider_actions()
        duplicates = set(actions).intersection(provider_actions)
        if duplicates:
            raise ValueError(f'Duplicate service actions: {", ".join(sorted(duplicates))}')
        actions.update(provider_actions)
        return actions

    def get_provider_actions(self):
        return {
            name: ('sync_provider', provider, action_class)
            for provider in self.registry.get_capable_providers('service_actions')
            if provider.is_authorized()
            for name, action_class in provider.service_action_classes.items()
        }

    def get_trakt_actions(self):
        from tmdbhelper.lib.script.actions.trakt.userlist import ItemUserList
        from tmdbhelper.lib.script.actions.trakt.comments import ItemComments
        return {name: ('trakt_api', self.trakt_api, action_class) for name, action_class in (
            ('userlist', ItemUserList), ('comments', ItemComments))}

    def get_item(self, name, *args):
        api_attribute, api, action_class = self.actions[name]
        item = action_class(*args)
        setattr(item, api_attribute, api)
        item.syncdata = self.syncdata
        return item
