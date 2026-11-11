import json
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting, set_setting
from tmdbhelper.lib.sync.providers.registry import SyncProviderRegistry


class RatingsProviderSettings:
    setting = 'ratings_provider_configuration'

    def __init__(self, registry=None):
        self.registry = registry if registry is not None else SyncProviderRegistry()

    @cached_property
    def configuration(self):
        return self.get_configuration()

    def get_configuration(self):
        value = get_setting(self.setting, 'str')
        return json.loads(value) if value else {}

    @property
    def order(self):
        return tuple(self.configuration.get('order', ()))

    @property
    def disabled(self):
        return tuple(self.configuration.get('disabled', ()))

    @cached_property
    def providers(self):
        return self.get_providers()

    def get_providers(self):
        priorities = {provider_id: index for index, provider_id in enumerate(self.order)}
        return tuple(sorted(
            self.registry.get_capable_providers('ratings'),
            key=lambda provider: (
                priorities.get(provider.provider_id, len(priorities)),
                provider.display_name.casefold(), provider.provider_id)))

    def get_enabled_providers(self, mediatype):
        return tuple(
            provider for provider in self.providers
            if provider.provider_id not in self.disabled and mediatype in provider.ratings_classes)

    def save(self, order, disabled):
        configuration = {
            'order': list(order) + [provider_id for provider_id in self.order if provider_id not in order],
            'disabled': sorted(disabled),
        }
        set_setting(self.setting, json.dumps(configuration), 'str')
