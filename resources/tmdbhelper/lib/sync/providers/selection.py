from tmdbhelper.lib.addon.plugin import get_setting, set_setting
from tmdbhelper.lib.sync.providers.features import FEATURE_LABELS


class SyncProviderSetting:
    never_value = 'never'

    def __init__(self, capability):
        self.capability = capability

    @property
    def setting(self):
        return f'sync_provider_{self.capability}'

    @property
    def value(self):
        return get_setting(self.setting, 'str')

    @property
    def is_unconfigured(self):
        return not self.value

    @property
    def is_never(self):
        return self.value == self.never_value

    @property
    def provider_id(self):
        value = self.value
        return '' if value == self.never_value else value

    def save(self, provider_id):
        if provider_id == self.value:
            return
        if self.capability != 'scrobbling':
            from tmdbhelper.lib.sync.invalidator import SyncInvalidatorAll
            invalidator = SyncInvalidatorAll()
            invalidator.features = (self.capability,)
            invalidator.notification = False
            invalidator.invalidate()
        set_setting(self.setting, provider_id, 'str')

    def disable(self):
        self.save(self.never_value)

    @classmethod
    def clear_provider(cls, provider_id):
        for capability in FEATURE_LABELS:
            setting = cls(capability)
            if setting.provider_id == provider_id:
                setting.save('')
