from xbmcgui import Dialog, DLG_YESNO_YES_BTN
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.provider_features import SyncProviderFeatureSelection
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class SyncProviderDefaultSelection(SyncProviderFeatureSelection):
    def select(self):
        selected = Dialog().yesnocustom(
            get_localized(32550), get_localized(32560).format(self.provider.display_name),
            yeslabel=get_localized(32561), nolabel=get_localized(222), customlabel=get_localized(32562),
            defaultbutton=DLG_YESNO_YES_BTN)
        if selected == 1:
            return self.set_default()
        if selected == 2:
            return super().select()

    def set_default(self):
        capabilities = self.capabilities
        # Kodi queues writes while settings is open, so set each final value only once.
        for feature in FEATURE_LABELS:
            provider_id = self.provider.provider_id if feature in capabilities else ''
            SyncProviderSetting(feature).save(provider_id)
