from xbmcgui import Dialog
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.method.sync_provider import SyncProviderSelection
from tmdbhelper.lib.sync.providers.scrobbling_settings import ScrobblingProviderSetting


class ScrobblingProviderSelection(SyncProviderSelection):
    @property
    def settings(self):
        return ScrobblingProviderSetting(self.capability)

    def get_preselect(self, ids):
        if self.is_unconfigured:
            preferred = super().get_preselect([self.never_value, *ids])
            return [preferred - 1] if preferred else []
        return [index for index, provider_id in enumerate(ids) if provider_id in self.settings.provider_ids]

    def select(self):
        providers = self.providers
        installers = self.get_installers()
        selected = Dialog().multiselect(
            self.heading,
            [provider.display_name for provider in providers] + [installer.label for installer in installers],
            preselect=self.get_preselect([provider.provider_id for provider in providers]))
        if selected is None:
            return
        selected_providers = []
        for index in selected:
            provider = self.get_selected_provider(index, installers)
            if provider is None:
                return
            selected_providers.append(provider.provider_id)
        self.settings.save_providers(selected_providers)
        return selected_providers

    def get_selected_provider(self, index, installers):
        if index < len(self.providers):
            provider = self.providers[index]
        else:
            provider = installers[index - len(self.providers)].install()
        if provider is None:
            return
        if self.capability not in provider.capabilities:
            Dialog().ok(get_localized(32550), get_localized(32554).format(provider.display_name, self.heading))
            return
        if self.confirm_provider(provider):
            return provider
