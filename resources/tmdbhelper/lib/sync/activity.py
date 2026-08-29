from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA, LASTACTIVITIES_EXPIRY
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.sync.mixins import SyncDataParentProperties


MDBLIST_SETTINGS = {
    'sync_source_watchlist': {
        'default': 'watchlisted_at'
    },
    'sync_source_collection': {
        'default': 'collected_at'
    },
    'sync_source_playback': {
        'default': 'paused_at',
        'episodes': 'episode_paused_at'
    },
    'sync_source_watched': {
        'default': 'watched_at',
        'shows': 'episode_watched_at',
        'episodes': 'episode_watched_at'
    },
}


class SyncLastActivities(SyncDataParentProperties):
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
        kodi_log('Sync: last_activities', 2)

        try:
            data = self.trakt_api.get_response_json('sync/last_activities') or {}
        except AttributeError:
            data = {}

        try:
            mdblist_data = self.mdblist_api.get_response_json('sync/last_activities') or {}
        except AttributeError:
            mdblist_data = {}

        if not data and not mdblist_data:
            return

        data = self.update_data_with_mdblist_activities(data, mdblist_data)

        data['expiry'] = set_timestamp(LASTACTIVITIES_EXPIRY)
        self.window.get_property(LASTACTIVITIES_DATA, set_property=data_dumps(data))

        return data

    @staticmethod
    def update_data_with_mdblist_activities(data, mdblist_data):
        for setting, keys in MDBLIST_SETTINGS.items():
            if get_setting(setting, 'str') != 'MDbList':
                continue
            for item_type in ('movies', 'shows', 'seasons', 'episodes'):
                activity_key = keys.get('default')
                activity_utc = mdblist_data.get(keys.get(item_type) or activity_key)
                data.setdefault(item_type, {})[activity_key] = activity_utc
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
