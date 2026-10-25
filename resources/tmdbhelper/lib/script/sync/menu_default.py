from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu
from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES, ITEM_ACTIONS
from tmdbhelper.lib.sync.datasync import SyncDataFactory


class Menu(BasicMenu):
    @cached_property
    def syncdata(self):
        return self.get_syncdata()

    def get_syncdata(self):
        return SyncDataFactory()

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return dict(self.get_provider_items(), **self.get_service_items())

    @cached_property
    def service_actions(self):
        from tmdbhelper.lib.script.actions.menu import ServiceActions
        return ServiceActions()

    @property
    def item_args(self):
        return (self.tmdb_type, self.tmdb_id, self.season, self.episode)

    def get_service_items(self):
        return {name: self.service_actions.get_item(name, *self.item_args)
                for name in self.service_actions.actions}

    def get_provider_items(self):
        registry = self.syncdata.registry
        items = {}
        for action in ITEM_ACTIONS:
            feature = ACTION_FEATURES[action]
            provider = registry.get_selected_provider(feature)
            if provider is not None and provider.is_authorized() and action in provider.action_classes:
                items[action] = self.create_provider_item(feature, provider, provider.action_classes[action])
        return items

    def create_provider_item(self, feature, provider, action_class):
        item = action_class(*self.item_args)
        item.syncdata = self.syncdata
        item.sync_feature = feature
        item.sync_provider = provider
        return item

    def item_get_self(self, item):
        return item.get_self()

    def choose(self):
        if not self.choices:
            return -1
        if len(self.choices) == 1:
            return 0
        from xbmcgui import Dialog
        return Dialog().contextmenu([self.get_choice_name(item) for item in self.choices])

    @staticmethod
    def get_choice_name(item):
        from tmdbhelper.lib.script.sync.provider import ItemSync
        service_name = item.sync_provider.display_name if isinstance(item, ItemSync) else item.service_name
        return f'{item.name} ({service_name})'

    def select(self, sync_type=None):
        if sync_type and sync_type not in self.items:
            return
        return super().select(sync_type)


def sync_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    Menu(tmdb_type, tmdb_id, season, episode).select(sync_type)
