from jurialmunkey.ftools import cached_property
from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.sync.providers.discovery import SyncProviderDiscovery
from tmdbhelper.lib.sync.providers.loader import SyncProviderLoader
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class SyncProviderRegistry:
    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        providers = {}
        for addon in SyncProviderDiscovery().addons:
            self.register_provider(providers, addon)
        return providers

    @staticmethod
    def register_provider(providers, addon):
        provider = SyncProviderLoader(addon).load()
        if provider.provider_id in providers:
            raise ValueError(f"Duplicate sync provider ID {provider.provider_id}: {addon['addonid']}")
        for registered in providers.values():
            duplicates = set(registered.list_routes).intersection(provider.list_routes)
            if duplicates:
                raise ValueError(f'Duplicate provider list routes: {", ".join(sorted(duplicates))}')
        providers[provider.provider_id] = provider

    def get_capable_providers(self, capability):
        return tuple(provider for provider in self.providers.values() if capability in provider.capabilities)

    def get_directory_items(self):
        return [
            provider.directory_item_class()
            for provider in self.providers.values()
            if provider.directory_item_class is not None
        ]

    def get_list_container(self, info, provider_id=None):
        providers = self.providers.values() if provider_id is None else (
            provider for provider in self.providers.values() if provider.provider_id == provider_id)
        for provider in providers:
            if info in provider.list_routes:
                return importmodule(**provider.list_routes[info])

    def get_selected_provider(self, capability):
        provider_id = self.get_selected_provider_id(capability)
        if not provider_id:
            return
        providers = self.providers
        try:
            provider = providers[provider_id]
        except KeyError:  # The selected addon may have been disabled or uninstalled.
            return
        if capability in provider.capabilities:
            return provider

    @staticmethod
    def get_selected_provider_id(capability):
        return SyncProviderSetting(capability).provider_id
