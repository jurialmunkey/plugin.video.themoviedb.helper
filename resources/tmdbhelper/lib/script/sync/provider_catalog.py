from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall
from tmdbhelper.lib.script.sync.provider_setup import SyncProviderOnboarding
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS


class SyncProviderCatalogueItem(SyncProviderInstall):
    @property
    def label(self):
        return self.get_label()

    def get_label(self):
        addon = self.get_addon()
        if addon is None:
            return get_localized(32558).format(self.display_name)
        if not addon['enabled']:
            return get_localized(32559).format(self.display_name)
        return self.display_name


class SyncProviderInstallSelection:
    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        providers = (SyncProviderCatalogueItem(addon_id) for addon_id in PROVIDERS)
        return sorted(providers, key=lambda provider: provider.display_name.casefold())

    def select(self):
        selected = Dialog().select(get_localized(32557), [provider.label for provider in self.providers])
        if selected == -1:
            return
        SyncProviderOnboarding(self.providers[selected].addon_id).configure()
