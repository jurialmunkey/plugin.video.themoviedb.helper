from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA, LASTACTIVITIES_EXPIRY
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.files.futils import json_dumps
from tmdbhelper.lib.sync.activity import SyncLastActivities


class TraktLastActivities(SyncLastActivities):
    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @property
    def json_property_name(self):
        return f'{LASTACTIVITIES_DATA}.trakt'

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.sync_last_activities.trakt.lockfile'

    def clear(self):
        self.clear_provider(self.window, 'trakt')

    def get_json_sync(self):
        data = self.instance_syncdata.core_sync.api.get_response_json('sync/last_activities')
        if data is None:
            return
        data['expiry'] = set_timestamp(LASTACTIVITIES_EXPIRY)
        self.window.get_property(self.json_property_name, set_property=json_dumps(data))
        return data
