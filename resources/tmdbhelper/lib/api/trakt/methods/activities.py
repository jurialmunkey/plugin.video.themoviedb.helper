from tmdbhelper.lib.addon.tmdate import set_timestamp
from jurialmunkey.window import get_property, WindowProperty
from tmdbhelper.lib.files.futils import json_loads as data_loads
from tmdbhelper.lib.files.futils import json_dumps as data_dumps
from tmdbhelper.lib.addon.thread import has_property_lock
from tmdbhelper.lib.api.trakt.decorators import is_authorized


LASTACTIVITIES_DATA = 'TraktSyncLastActivities'
LASTACTIVITIES_LOCK = 'TraktSyncLastActivities.Locked'
LASTACTIVITIES_EXPIRY = 'TraktSyncLastActivities.Expires'
LASTACTIVITIES_EXPIRY_SECONDS = 120


@is_authorized
def get_last_activity(self, activity_type=None, activity_key=None, cache_refresh=False, cache_only=False, skip_online=False):

    def _cache_expired():
        """ Check if the cached last_activities has expired """
        if self.last_activities_expires:
            if self.last_activities_expires < set_timestamp(0, True):
                return True
            return False

        self.last_activities_expires = get_property(LASTACTIVITIES_EXPIRY, is_type=int) or -1
        return _cache_expired()  # Check again using property

    def _cache_activity():
        """ Get last_activities from Trakt and add to cache while locking other lookup threads """
        with WindowProperty((LASTACTIVITIES_LOCK, 1)):
            response = self.get_response_json('sync/last_activities')  # Retrieve data from Trakt
            if response:
                get_property(LASTACTIVITIES_DATA, set_property=data_dumps(response))  # Dump data to property
                get_property(LASTACTIVITIES_EXPIRY, set_property=set_timestamp(LASTACTIVITIES_EXPIRY_SECONDS, True))  # Set activity expiry
        return response

    def _cache_router():
        """ Routes between getting cached object or new lookup """

        if not _cache_expired():
            return self.last_activities or data_loads(get_property(LASTACTIVITIES_DATA))

        if skip_online and self.last_activities_expires == -1:
            return self.last_activities or data_loads(get_property(LASTACTIVITIES_DATA))

        if has_property_lock(LASTACTIVITIES_LOCK):  # Other thread getting data so wait for it
            return data_loads(get_property(LASTACTIVITIES_DATA))

        return _cache_activity()

    if cache_only:  # If we are not authorized
        return -1

    self.last_activities = _cache_router() or {}

    def _get_activity_timestamp(activities):
        if not activities and skip_online:
            return '0000-00-00T00:00:00.000000Z'
        if not activity_type:
            return activities.get('all', '')
        if not activity_key:
            return activities.get(activity_type, {})
        return activities.get(activity_type, {}).get(activity_key, '')

    return _get_activity_timestamp(self.last_activities)
