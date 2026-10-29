from xbmcgui import Dialog, DLG_YESNO_NO_BTN
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.provider_install import SyncProviderInstall
from tmdbhelper.lib.script.sync.provider_settings import SyncProviderSettings
from tmdbhelper.lib.sync.providers.catalog import PROVIDERS
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting, SyncProviderSettingFactory


class SyncProviderSelection(SyncProviderSetting):
    @property
    def capabilities(self):
        return (self.capability,)

    @property
    def heading(self):
        return ' / '.join(get_localized(FEATURE_LABELS[feature]) for feature in self.capabilities)

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        providers = (provider for provider in SyncProviderRegistry().providers.values()
                     if set(self.capabilities).intersection(provider.capabilities))
        return sorted(providers, key=lambda provider: (provider.display_name.casefold(), provider.provider_id))

    def get_installers(self):
        capabilities = set(self.capabilities)
        installers = (SyncProviderInstall(addon_id) for addon_id in PROVIDERS)
        return sorted((installer for installer in installers
                       if capabilities.intersection(installer.capabilities) and not installer.is_available),
                      key=lambda installer: installer.display_name.casefold())

    def get_preselect(self, ids):
        if not self.is_unconfigured:
            return ids.index(self.value) if self.value in ids else 0
        selected_ids = {
            provider_id for feature in FEATURE_LABELS if feature not in self.capabilities
            for provider_id in SyncProviderSettingFactory(feature).provider_ids}
        preferred = next((provider.provider_id for provider in self.providers
                          if provider.provider_id in selected_ids), self.never_value)
        return ids.index(preferred)

    def select(self):
        ids = [self.never_value, *(provider.provider_id for provider in self.providers)]
        labels = [get_localized(231), *(provider.display_name for provider in self.providers)]
        installers = self.get_installers()
        labels.extend(installer.label for installer in installers)
        selected = Dialog().select(self.heading, labels, preselect=self.get_preselect(ids))
        if selected == -1:
            return
        if selected >= len(ids):
            return self.select_installer(installers[selected - len(ids)])
        if selected and not self.confirm_provider(self.providers[selected - 1]):
            return
        self.save(ids[selected])
        return ids[selected]

    def confirm_provider(self, provider):
        if provider.addon_id in PROVIDERS:
            return True
        return Dialog().yesno(
            get_localized(32550), get_localized(32563).format(provider.display_name),
            yeslabel=get_localized(186), nolabel=get_localized(222),
            defaultbutton=DLG_YESNO_NO_BTN)

    def select_installer(self, installer):
        provider = installer.install()
        if provider is None:
            return
        if not set(self.capabilities).intersection(provider.capabilities):
            Dialog().ok(get_localized(32550), get_localized(32554).format(provider.display_name, self.heading))
            return
        self.save_provider(provider)
        return provider.provider_id

    def save_provider(self, provider):
        self.save(provider.provider_id)


class SyncProviderListSelection(SyncProviderSelection):
    def __init__(self, capabilities):
        super().__init__(capabilities[0])
        self._capabilities = capabilities

    @property
    def capabilities(self):
        return self._capabilities

    def save(self, provider_id):
        if provider_id == self.never_value:
            for capability in self.capabilities:
                SyncProviderSetting(capability).disable()
            return
        provider = SyncProviderRegistry().providers[provider_id]
        self.save_provider(provider)

    def save_provider(self, provider):
        capability = next(feature for feature in self.capabilities if feature in provider.capabilities)
        SyncProviderSetting(capability).save(provider.provider_id)


def select_sync_provider(capability, return_settings=False, **kwargs):
    if capability == 'scrobbling':
        from tmdbhelper.lib.script.sync.scrobbling import ScrobblingProviderSelection
        selection = ScrobblingProviderSelection(capability)
    else:
        selection = SyncProviderSelection(capability)
    if return_settings:
        return SyncProviderSettings(FEATURE_LABELS[capability]).select(selection)
    selection.select()


def configure_sync_provider(addon_id, **kwargs):
    from tmdbhelper.lib.script.sync.provider_setup import SyncProviderOnboarding
    SyncProviderOnboarding(addon_id).configure()


def install_sync_provider(return_settings=False, **kwargs):
    from tmdbhelper.lib.script.sync.provider_catalog import SyncProviderInstallSelection
    selection = SyncProviderInstallSelection()
    if return_settings:
        return SyncProviderSettings(32557).select(selection)
    selection.select()


def open_sync_provider_settings(addon_id, **kwargs):
    from xbmcaddon import Addon
    provider = SyncProviderInstall(addon_id).install()
    if provider is not None:
        Addon(provider.addon_id).openSettings()
