from tmdbhelper.lib.addon.plugin import executebuiltin, get_localized
from tmdbhelper.lib.sync.providers.addon import SyncProviderAddon
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS


class SyncProviderInstall(SyncProviderAddon):
    @property
    def display_name(self):
        return PROVIDERS[self.addon_id]['display_name']

    @property
    def capabilities(self):
        return PROVIDERS[self.addon_id]['capabilities']

    @property
    def label(self):
        addon = self.get_addon()
        localized = 32551 if addon is None else 32552
        return get_localized(localized).format(self.display_name)

    @property
    def is_available(self):
        addon = self.get_addon()
        return addon is not None and addon['enabled']

    def install(self):
        if self.get_addon() is None:
            executebuiltin(f'InstallAddon({self.addon_id})', wait=True)
        addon = self.get_addon()
        if addon is not None and not addon['enabled']:
            executebuiltin(f'EnableAddon({self.addon_id})', wait=True)
        return self.get_provider()
