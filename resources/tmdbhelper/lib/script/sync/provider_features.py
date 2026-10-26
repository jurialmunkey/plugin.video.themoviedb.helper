from xbmcgui import Dialog
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class SyncProviderFeatureSelection:
    def __init__(self, provider):
        self.provider = provider

    @property
    def capabilities(self):
        return tuple(feature for feature in FEATURE_LABELS if feature in self.provider.capabilities)

    def select(self):
        settings = tuple(SyncProviderSetting(feature) for feature in self.capabilities)
        preselect = [index for index, setting in enumerate(settings)
                     if setting.provider_id == self.provider.provider_id]
        selected = Dialog().multiselect(
            get_localized(32553).format(self.provider.display_name),
            [get_localized(FEATURE_LABELS[setting.capability]) for setting in settings],
            preselect=preselect)
        if selected is None:
            return
        for index, setting in enumerate(settings):
            self.save_selection(setting, index in selected)

    def save_selection(self, setting, selected):
        if selected:
            setting.save(self.provider.provider_id)
        elif setting.provider_id == self.provider.provider_id:
            setting.save('')
