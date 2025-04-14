from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA
from tmdbhelper.lib.files.locker import mutexlock


LASTACTIVITIES_EXPIRY = 600


class SyncLastActivities:
    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.sync_last_activities.lockfile'

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

    def __init__(self, class_instance_syncdata):
        self.class_instance_syncdata = class_instance_syncdata

    @property
    def cache(self):
        return self.class_instance_syncdata.cache

    @property
    def window(self):
        return self.class_instance_syncdata.window

    @property
    def get_response_json(self):
        return self.class_instance_syncdata.get_response_json

    def get_json(self):
        return self.json_prop or self.json_data or {}

    @mutexlock
    def get_json_data(self):
        return self.json_prop or self.json_sync or {}

    def get_json_prop(self):
        data = data_loads(self.window.get_property(LASTACTIVITIES_DATA))
        if not data or not get_timestamp(data.get('expiry') or 0):
            return
        return data

    def get_json_sync(self):
        from tmdbhelper.lib.addon.logger import kodi_log
        kodi_log('Sync: last_activities', 2)
        data = self.get_response_json('sync/last_activities')
        if not data:
            return
        data['expiry'] = set_timestamp(LASTACTIVITIES_EXPIRY)
        self.window.get_property(LASTACTIVITIES_DATA, set_property=data_dumps(data))
        return data

    def is_expired(self, timestamp, keys=None):
        if not timestamp:
            return True

        last_activity = self.json

        if not last_activity:
            return True

        for k in (keys or ('all', )):
            last_activity = last_activity.get(k) or {}

        if not last_activity or last_activity > timestamp:
            return True

        return False
