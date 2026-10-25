from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized, get_setting, set_setting
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry


class SyncProviderSelection:
    def __init__(self, capability):
        self.capability = capability

    @property
    def setting(self):
        return f'sync_provider_{self.capability}'

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        providers = SyncProviderRegistry().get_capable_providers(self.capability)
        return sorted(providers, key=lambda provider: (provider.display_name.casefold(), provider.provider_id))

    def select(self):
        ids = ['', *(provider.provider_id for provider in self.providers)]
        labels = [get_localized(231), *(provider.display_name for provider in self.providers)]
        current = get_setting(self.setting, 'str')
        preselect = ids.index(current) if current in ids else 0
        selected = Dialog().select(get_localized(FEATURE_LABELS[self.capability]), labels, preselect=preselect)
        if selected == -1 or ids[selected] == current:
            return
        self.save(ids[selected])

    def save(self, provider_id):
        if self.capability != 'scrobbling':
            from tmdbhelper.lib.sync.invalidator import SyncInvalidatorAll
            invalidator = SyncInvalidatorAll()
            invalidator.features = (self.capability,)
            invalidator.notification = False
            invalidator.invalidate()
        set_setting(self.setting, provider_id, 'str')


def select_sync_provider(capability, **kwargs):
    SyncProviderSelection(capability).select()
