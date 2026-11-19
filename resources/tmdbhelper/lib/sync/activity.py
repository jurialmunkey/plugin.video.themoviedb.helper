from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA, LASTACTIVITIES_EXPIRY
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.sync.mixins import SyncDataParentProperties


class SyncLastActivities(SyncDataParentProperties):
    def __init__(self, instance_syncdata, provider):
        super().__init__(instance_syncdata)
        self.provider = provider

    @staticmethod
    def get_property_name(provider_id):
        return f'{LASTACTIVITIES_DATA}.{provider_id}'

    @property
    def json_property_name(self):
        return self.get_property_name(self.provider.provider_id)

    def clear(self):
        self.clear_provider(self.window, self.provider.provider_id)

    @classmethod
    def clear_provider(cls, window, provider_id):
        window.get_property(cls.get_property_name(provider_id), clear_property=True)

    @staticmethod
    def is_current_data(data):
        return bool(data and get_timestamp(data.get('expiry') or 0))

    @classmethod
    def get_provider_marker(cls, window, provider_id):
        """The provider's stored last activities while they are current, otherwise None.
        Changes that need a new sync clear them, so an unchanged marker means synced data is fresh."""
        marker = window.get_property(cls.get_property_name(provider_id))
        if not cls.is_current_data(data_loads(marker)):
            return
        return marker

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.sync_last_activities.{self.provider.provider_id}.lockfile'

    @cached_property
    def json(self):
        return self.get_json()

    @cached_property
    def json_data(self):
        return self.get_json_data()

    @cached_property
    def json_prop(self):
        return self.get_json_prop()

    @cached_property
    def json_sync(self):
        return self.get_json_sync()

    def get_json(self):
        return self.json_prop or self.json_data or {}

    @mutexlock
    def get_json_data(self):
        # Re-read the shared cache after waiting for another caller to refresh it.
        return self.get_json_prop() or self.json_sync or {}

    def get_json_prop(self):
        data = data_loads(self.window.get_property(self.json_property_name))
        if not self.is_current_data(data):
            return
        return data

    def get_json_sync(self):
        data = self.provider.get_last_activities()
        if data is None:
            return
        data['expiry'] = set_timestamp(LASTACTIVITIES_EXPIRY)
        self.window.get_property(self.json_property_name, set_property=data_dumps(data))
        return data

    def is_expired(self, timestamp, keys=None):
        if not timestamp:
            return True

        last_activity = self.get_last_activity(keys)

        if last_activity and last_activity > timestamp:
            return True

        return False

    def get_last_activity(self, keys=None):
        last_activity = self.json

        if not last_activity:
            return

        for k in (keys or ('all', )):
            last_activity = last_activity.get(k) or {}

        return last_activity
