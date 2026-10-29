from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.actions.menu import ServiceActions
from tmdbhelper.lib.sync.datasync import SyncDataFactory
from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, ITEM_ACTIONS


class ActionDiscovery:
    def __init__(self, syncdata=None):
        self.syncdata = syncdata if syncdata is not None else SyncDataFactory()

    @cached_property
    def service_actions(self):
        return self.get_service_actions()

    def get_service_actions(self):
        return ServiceActions(self.syncdata.registry, syncdata=self.syncdata)

    @cached_property
    def provider_actions(self):
        return self.get_provider_actions()

    def get_provider_actions(self):
        actions = {}
        for name in ITEM_ACTIONS:
            feature = ACTION_FEATURES[name]
            provider = self.syncdata.registry.get_selected_provider(feature)
            if provider is not None and provider.is_authorized() and name in provider.action_classes:
                actions[name] = (feature, provider, provider.action_classes[name])
        return actions

    @cached_property
    def is_available(self):
        return self.get_is_available()

    def get_is_available(self):
        return bool(self.service_actions.actions or self.provider_actions)

    def get_provider_item(self, name, *args):
        feature, provider, action_class = self.provider_actions[name]
        item = action_class(*args)
        item.syncdata = self.syncdata
        item.sync_feature = feature
        item.sync_provider = provider
        return item

    def get_items(self, *args):
        items = {name: self.get_provider_item(name, *args) for name in self.provider_actions}
        items.update((name, self.service_actions.get_item(name, *args)) for name in self.service_actions.actions)
        return items
