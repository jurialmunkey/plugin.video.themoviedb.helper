from xbmcgui import Dialog, DLG_YESNO_NO_BTN
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.script.sync.provider_features import SyncProviderFeatureSelection
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS
from tmdbhelper.lib.sync.providers.ratings_settings import RatingsProviderSettings
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting, SyncProviderSettingFactory


class SyncProviderManagerFeatures(SyncProviderFeatureSelection):
    @property
    def sync_features(self):
        return tuple(feature for feature in FEATURE_LABELS if feature != 'scrobbling')

    @property
    def active_features(self):
        return self.get_active_features()

    def get_active_features(self):
        labels = [
            get_localized(label) for feature, label in FEATURE_LABELS.items()
            if self.provider.provider_id in SyncProviderSettingFactory(feature).provider_ids]
        if 'ratings' in self.provider.capabilities and self.provider.provider_id not in RatingsProviderSettings().disabled:
            labels.append(get_localized(32581))
        return labels

    def set_ratings_enabled(self, enabled):
        settings = RatingsProviderSettings()
        disabled = set(settings.disabled)
        if enabled:
            disabled.discard(self.provider.provider_id)
        else:
            disabled.add(self.provider.provider_id)
        settings.save(settings.order, disabled)

    def clear(self):
        SyncProviderSetting.clear_provider(self.provider.provider_id)
        if 'ratings' in self.provider.capabilities:
            self.set_ratings_enabled(False)


class SyncProviderManagerSetup(SyncProviderManagerFeatures):
    def select(self):
        self.select_default()
        if 'ratings' in self.provider.capabilities:
            self.select_ratings()
        if 'scrobbling' in self.provider.capabilities:
            self.select_scrobbling()

    def select_default(self):
        if not set(self.sync_features).intersection(self.provider.capabilities):
            return
        if not Dialog().yesno(
                get_localized(32740), get_localized(32742).format(self.provider.display_name),
                defaultbutton=DLG_YESNO_NO_BTN):
            return
        for feature in self.sync_features:
            provider_id = self.provider.provider_id if feature in self.provider.capabilities else ''
            SyncProviderSettingFactory(feature).save(provider_id)

    def select_ratings(self):
        enabled = Dialog().yesno(
            get_localized(32740), get_localized(32743).format(self.provider.display_name),
            defaultbutton=DLG_YESNO_NO_BTN)
        self.set_ratings_enabled(enabled)

    def select_scrobbling(self):
        enabled = Dialog().yesno(
            get_localized(32740), get_localized(32744).format(self.provider.display_name),
            defaultbutton=DLG_YESNO_NO_BTN)
        setting = SyncProviderSettingFactory('scrobbling')
        if enabled:
            setting.add_provider(self.provider.provider_id)
        else:
            setting.remove_provider(self.provider.provider_id)
