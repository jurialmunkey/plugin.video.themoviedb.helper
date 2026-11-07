"""Share whether sync actions are available between Kodi's add-on processes."""

from jurialmunkey.ftools import cached_property
from jurialmunkey.window import WindowPropertySetter
from tmdbhelper.lib.addon.plugin import get_version
from tmdbhelper.lib.addon.tmdate import get_timestamp, set_timestamp
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.sync.providers.features import ACTION_FEATURES
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class SyncActionsAvailability:
    """Whether any sync actions are available, without loading provider add-ons each time.

    Working the answer out loads provider add-ons, so it is kept in a window property for
    expiry seconds, as provider last activities are. It is tied to the selected providers
    and the add-on version: changing either, including signing out, works it out again.
    Signing in or installing a provider without changing the selection is noticed when the
    stored answer expires.

    discovery_source provides action_discovery, which is only loaded to work the answer out.
    """

    property_name = 'SyncActions.Available'
    expiry = 600

    def __init__(self, discovery_source):
        self.discovery_source = discovery_source

    @cached_property
    def window(self):
        return WindowPropertySetter()

    @cached_property
    def fingerprint(self):
        return self.get_fingerprint()

    def get_fingerprint(self):
        return {
            'version': get_version(),
            'providers': {
                feature: SyncProviderSetting(feature).provider_id
                for feature in sorted(set(ACTION_FEATURES.values()))
            },
        }

    @cached_property
    def stored(self):
        return data_loads(self.window.get_property(self.property_name)) or {}

    @property
    def is_stored_current(self):
        return bool(
            self.stored.get('fingerprint') == self.fingerprint
            and get_timestamp(self.stored.get('expiry') or 0)
        )

    @cached_property
    def is_available(self):
        return self.get_is_available()

    def get_is_available(self):
        if self.is_stored_current:
            return self.stored['available']
        available = self.discovery_source.action_discovery.is_available
        self.store(available)
        return available

    def store(self, available):
        self.window.get_property(self.property_name, set_property=data_dumps({
            'available': available,
            'fingerprint': self.fingerprint,
            'expiry': set_timestamp(self.expiry, True),
        }))
