from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import get_jsonrpc
from tmdbhelper.lib.sync.providers.addon import SyncProviderAddon
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS
from tmdbhelper.lib.sync.providers.discovery import SyncProviderDiscovery


class SyncProviderModuleDiscovery(SyncProviderDiscovery):
    def get_addons(self):
        response = get_jsonrpc('Addons.GetAddons', {
            'type': 'xbmc.python.module',
            'enabled': 'all',
            'installed': True,
            'properties': ['path', 'enabled', 'name'],
        })
        return tuple(
            addon for addon in response['result'].get('addons', ())
            if addon['addonid'].startswith(self.addon_prefix))

    def get_modules(self):
        addons = {addon['addonid']: addon for addon in self.addons}
        modules = (
            SyncProviderModule(addon_id, addons.get(addon_id))
            for addon_id in addons.keys() | PROVIDERS.keys())
        return sorted(modules, key=lambda module: (module.display_name.casefold(), module.addon_id))


class SyncProviderModule(SyncProviderAddon):
    def __init__(self, addon_id, addon):
        super().__init__(addon_id)
        self.addon = addon

    @property
    def display_name(self):
        if self.addon_id in PROVIDERS:
            return PROVIDERS[self.addon_id]['display_name']
        return self.addon['name']

    @property
    def is_enabled(self):
        return self.addon is not None and self.addon['enabled']

    @cached_property
    def provider(self):
        return self.get_provider()

    def enable(self):
        self.set_enabled(True)
        return self.get_provider()

    def set_enabled(self, enabled):
        response = get_jsonrpc('Addons.SetAddonEnabled', {
            'addonid': self.addon_id,
            'enabled': enabled,
        })
        if response.get('result') != 'OK':
            raise RuntimeError(f'Unable to change provider module {self.addon_id}: {response}')
        addon = self.get_addon()
        if addon is None or addon['enabled'] != enabled:
            raise RuntimeError(f'Provider module {self.addon_id} did not change enabled state')
