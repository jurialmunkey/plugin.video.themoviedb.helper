from jurialmunkey.ftools import cached_property
from jurialmunkey.modimp import importmodule
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.sync.providers.discovery import SyncProviderDiscovery
from tmdbhelper.lib.sync.providers.loader import SyncProviderLoader, SyncProviderLoadError
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting, SyncProviderSettingFactory


class SyncProviderRegistry:
    @cached_property
    def discovery(self):
        return self.get_discovery()

    def get_discovery(self):
        return SyncProviderDiscovery()

    @cached_property
    def internal_providers(self):
        return self.get_internal_providers()

    def get_internal_providers(self):
        from tmdbhelper.lib.sync.providers.omdb import Provider as OMDbProvider
        from tmdbhelper.lib.sync.providers.tmdb import Provider as TMDbProvider
        providers = {}
        for provider_class in (TMDbProvider, OMDbProvider):
            provider = provider_class()
            SyncProviderLoader({'addonid': provider.addon_id}).validate_provider(provider)
            if provider.is_authorized():
                self.register_provider(providers, provider)
        return providers

    @cached_property
    def loaded_providers(self):
        """Providers loaded so far by addon ID, shared by single and full loading."""
        return {}

    @cached_property
    def failed_providers(self):
        """Load errors by addon ID. A failed addon is not retried by this registry."""
        return {}

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        providers = dict(self.internal_providers)
        loaded = (self.find_addon_provider(addon) for addon in self.discovery.addons)
        for provider in (provider for provider in loaded if provider is not None):
            self.register_provider(providers, provider)
        return providers

    def find_addon_provider(self, addon):
        """Return the addon's provider, or None while it cannot be loaded."""
        try:
            return self.load_provider(addon)
        except SyncProviderLoadError:
            return

    def load_provider(self, addon):
        """Raises SyncProviderLoadError if the addon cannot be loaded, such as while
        TMDbHelper and the provider addon are updated separately."""
        addon_id = addon['addonid']
        try:
            return self.loaded_providers[addon_id]
        except KeyError:
            pass
        if addon_id in self.failed_providers:
            raise self.failed_providers[addon_id]
        from tmdbhelper.lib.script.sync.provider_errors import SyncProviderLoadErrorDialog
        try:
            provider = self.loaded_providers[addon_id] = SyncProviderLoader(addon).load()
        except SyncProviderLoadError as exc:
            self.failed_providers[addon_id] = exc
            kodi_log(f'{exc}. The provider is unavailable until it loads.', 1)
            SyncProviderLoadErrorDialog(addon_id).show()
            raise
        SyncProviderLoadErrorDialog(addon_id).clear()
        return provider

    def get_provider(self, provider_id):
        """Return internal providers without addon discovery.
        Load only the provider's own addon when its ID follows the addon naming convention.
        Other providers are found by loading every provider. Raises KeyError if unavailable,
        or SyncProviderLoadError if the provider's own addon cannot be loaded."""
        try:
            return self.internal_providers[provider_id]
        except KeyError:
            pass
        addon = self.discovery.get_addon(provider_id)
        if addon is None:
            return self.providers[provider_id]
        provider = self.load_provider(addon)
        if provider.provider_id != provider_id:
            return self.providers[provider_id]
        return provider

    def find_provider(self, provider_id):
        try:
            return self.get_provider(provider_id)
        except KeyError:  # The selected addon may have been disabled or uninstalled.
            return
        except SyncProviderLoadError:  # The selected addon may be partway through an update.
            return

    def is_provider_unavailable(self, provider_id):
        """Whether the provider's addon is installed but cannot currently be loaded.
        Unlike a missing provider, its synced data is still valid and must be kept."""
        try:
            self.get_provider(provider_id)
        except KeyError:
            return False
        except SyncProviderLoadError:
            return True
        return False

    @staticmethod
    def register_provider(providers, provider):
        if provider.provider_id in providers:
            raise ValueError(f"Duplicate sync provider ID {provider.provider_id}: {provider.addon_id}")
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
        provider = self.find_provider(provider_id)
        if provider is not None and capability in provider.capabilities:
            return provider

    def get_selected_providers(self, capability):
        provider_ids = SyncProviderSettingFactory(capability).provider_ids
        return tuple(
            provider for provider_id in provider_ids
            if (provider := self.find_provider(provider_id)) is not None
            and capability in provider.capabilities)

    @staticmethod
    def get_selected_provider_id(capability):
        return SyncProviderSetting(capability).provider_id
