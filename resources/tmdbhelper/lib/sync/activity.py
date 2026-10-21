from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA, LASTACTIVITIES_EXPIRY
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.sync.mixins import SyncDataParentProperties


SOURCE_ACTIVITIES = {
    'watchlisted_at': {
        'setting': 'sync_source_watchlist'
    },
    'collected_at': {
        'setting': 'sync_source_collection'
    },
    'paused_at': {
        'setting': 'sync_source_watched',
        'episodes': 'episode_paused_at'
    },
    'watched_at': {
        'setting': 'sync_source_watched',
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
        if data.get('floppy_reload') != self.floppy_reload:  # Floppy data changed by another add-on
            return
        return data

    @cached_property
    def floppy_reload(self):
        from tmdbhelper.lib.api.floppy.api import get_floppy_reload
        return get_floppy_reload()

    def get_json_sync(self):
        kodi_log('Sync: last_activities', 2)

        try:
            data = self.trakt_api.get_response_json('sync/last_activities') or {}
        except AttributeError:
            data = {}

        source_data = {
            'MDbList': self.get_mdblist_activities(),
            'Floppy': self.get_floppy_activities(),
        }

        if not data and not any(source_data.values()):
            return

        data = self.update_data_with_source_activities(data, source_data)

        data['expiry'] = set_timestamp(LASTACTIVITIES_EXPIRY)
        data['floppy_reload'] = self.floppy_reload
        self.window.get_property(LASTACTIVITIES_DATA, set_property=data_dumps(data))

        return data

    def get_mdblist_activities(self):
        try:
            return self.mdblist_api.get_response_json('sync/last_activities') or {}
        except AttributeError:
            return {}

    def get_floppy_activities(self):
        if not self.floppy_api:
            return {}
        if not any(get_setting(keys['setting'], 'str') == 'Floppy' for keys in SOURCE_ACTIVITIES.values()):
            return {}
        from tmdbhelper.lib.sync.floppy.activity import FloppyLastActivities
        return FloppyLastActivities(self.floppy_api).data

    @staticmethod
    def update_data_with_source_activities(data, source_data):
        """ Replace Trakt activities with those of the source selected for each sync type """
        for activity_key, keys in SOURCE_ACTIVITIES.items():
            try:
                activities = source_data[get_setting(keys['setting'], 'str')]
            except KeyError:  # Trakt
                continue
            for item_type in ('movies', 'shows', 'seasons', 'episodes'):
                activity_utc = activities.get(keys.get(item_type) or activity_key)
                data.setdefault(item_type, {})[activity_key] = activity_utc
        try:
            activities = source_data[get_setting('sync_source_watched', 'str')]
        except KeyError:  # Trakt
            return data
        data.setdefault('shows', {})['dropped_at'] = activities.get('dropped_at')
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
