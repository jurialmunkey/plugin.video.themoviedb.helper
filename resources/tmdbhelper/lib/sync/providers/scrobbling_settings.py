import json
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class ScrobblingProviderSetting(SyncProviderSetting):
    @property
    def provider_ids(self):
        value = self.value
        if not value or value == self.never_value:
            return ()
        return tuple(json.loads(value)) if value.startswith('[') else (value,)

    def save_providers(self, provider_ids):
        value = json.dumps(list(dict.fromkeys(provider_ids))) if provider_ids else self.never_value
        super().save(value)

    def add_provider(self, provider_id):
        self.save_providers((*self.provider_ids, provider_id))

    def remove_provider(self, provider_id):
        if provider_id not in self.provider_ids:
            return
        remaining = tuple(value for value in self.provider_ids if value != provider_id)
        if remaining:
            self.save_providers(remaining)
        else:
            self.save('')
