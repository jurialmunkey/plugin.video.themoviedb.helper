"""Share whether sync actions are available between Kodi's add-on processes."""

from threading import Lock
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

    Each stored answer is also published for skins as a plain boolean property, which is
    True when the sync options menu has actions and empty otherwise.

    discovery_source provides action_discovery, which is only loaded to work the answer out.
    """

    property_name = 'SyncActions.Available'
    skin_property_name = 'SyncActions.IsAvailable'
    expiry = 600

    def __init__(self, discovery_source):
        self.discovery_source = discovery_source

    @cached_property
    def window(self):
        return WindowPropertySetter()

    @property
    def action_discovery(self):
        return self.discovery_source.action_discovery

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
    def is_fingerprint_current(self):
        return self.stored.get('fingerprint') == self.fingerprint

    @property
    def is_stored_current(self):
        return bool(
            self.is_fingerprint_current
            and get_timestamp(self.stored.get('expiry') or 0)
        )

    @cached_property
    def is_available(self):
        return self.get_is_available()

    def get_is_available(self):
        if self.is_stored_current:
            return self.stored['available']
        available = self.action_discovery.is_available
        self.store(available)
        return available

    def store(self, available):
        self.window.get_property(self.property_name, set_property=data_dumps({
            'available': available,
            'fingerprint': self.fingerprint,
            'expiry': set_timestamp(self.expiry, True),
        }))
        self.publish(available)

    def publish(self, available):
        self.window.get_property(
            self.skin_property_name,
            set_property='True' if available else None,
            clear_property=not available,
        )


class SyncActionsAvailabilityRefresh(SyncActionsAvailability):
    """Work the answer out again in the service and publish it, ignoring any stored answer.

    The service has no listing to provide action_discovery, so it discovers actions itself.
    Refreshes share one lock so the last answer stored belongs to the latest selection.
    """

    is_stored_current = False
    refresh_lock = Lock()

    def __init__(self, syncdata=None):
        super().__init__(discovery_source=None)
        self.syncdata = syncdata

    @cached_property
    def action_discovery(self):
        return self.get_action_discovery()

    def get_action_discovery(self):
        from tmdbhelper.lib.script.actions.discovery import ActionDiscovery
        return ActionDiscovery(self.syncdata)

    def refresh(self):
        with self.refresh_lock:
            return self.is_available


class SyncActionsAvailabilitySelectionRefresh(SyncActionsAvailabilityRefresh):
    """Work the answer out again only when the selected providers or add-on version changed."""

    @property
    def is_stored_current(self):
        return self.is_fingerprint_current
