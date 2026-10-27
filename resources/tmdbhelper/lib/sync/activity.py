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

    @property
    def json_property_name(self):
        return f'{LASTACTIVITIES_DATA}.{self.provider.provider_id}'

    def clear(self):
        self.clear_provider(self.window, self.provider.provider_id)

    @staticmethod
    def clear_provider(window, provider_id):
        window.get_property(f'{LASTACTIVITIES_DATA}.{provider_id}', clear_property=True)

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
        if not data or not get_timestamp(data.get('expiry') or 0):
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
