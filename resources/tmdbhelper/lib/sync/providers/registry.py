from jurialmunkey.ftools import cached_property
from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.sync.providers.discovery import SyncProviderDiscovery
from tmdbhelper.lib.sync.providers.loader import SyncProviderLoader
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting, SyncProviderSettingFactory


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
            duplicates = set(registered.service_action_classes).intersection(provider.service_action_classes)
            if duplicates:
                raise ValueError(f'Duplicate provider service actions: {", ".join(sorted(duplicates))}')
            duplicates = set(registered.service_sync_classes).intersection(provider.service_sync_classes)
            if duplicates:
                raise ValueError(f'Duplicate provider service sync types: {", ".join(sorted(duplicates))}')
        providers[provider.provider_id] = provider

    def get_capable_providers(self, capability):
        return tuple(provider for provider in self.providers.values() if capability in provider.capabilities)

    def get_service_sync_provider(self, sync_type):
        return next((
            provider for provider in self.providers.values()
            if sync_type in provider.service_sync_classes), None)

    @cached_property
    def monitor_list_suppliers(self):
        return self.get_monitor_list_suppliers()

    def get_monitor_list_suppliers(self):
        return tuple(
            provider.monitor_lists_class(provider)
            for provider in self.get_capable_providers('monitor_lists'))

    def get_monitor_list_supplier(self, user_slug):
        return next((supplier for supplier in self.monitor_list_suppliers if supplier.user_slug == user_slug), None)

    def get_monitor_list_reference(self, user_slug, list_slug):
        supplier = self.get_monitor_list_supplier(user_slug)
        if supplier is not None:
            return supplier, list_slug
        for supplier in self.monitor_list_suppliers:
            translated = supplier.get_legacy_list_slug(user_slug, list_slug)
            if translated is not None:
                return supplier, translated

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

    def get_selected_providers(self, capability):
        provider_ids = SyncProviderSettingFactory(capability).provider_ids
        return tuple(
            provider for provider_id in provider_ids
            if (provider := self.providers.get(provider_id)) is not None
            and capability in provider.capabilities)

    @staticmethod
    def get_selected_provider_id(capability):
        return SyncProviderSetting(capability).provider_id
