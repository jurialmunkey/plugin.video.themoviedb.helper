from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.floppy.dataconf import FLOPPY_STATUS_PLANNING, FLOPPY_STATUS_COMPLETED, FLOPPY_STATUS_DROPPED


class FloppyActivity:
    """
    Newest timestamp of one Floppy list
    Removals do not change the newest timestamp so the list is fingerprinted by its total and newest entry
    A changed fingerprint is reported as now so that any change since the last check resyncs
    """

    def __init__(self, floppy_api, name, *args, key='created_at', **kwargs):
        self.floppy_api = floppy_api
        self.name = name
        self.args = args
        self.key = key
        self.kwargs = kwargs

    @cached_property
    def response(self):
        return self.floppy_api.get_response_json(*self.args, limit=1, **self.kwargs)

    @cached_property
    def newest(self):
        try:
            return self.response['results'][0][self.key]
        except (KeyError, IndexError):  # Failed request or empty list
            return

    @cached_property
    def fingerprint(self):
        try:
            return f'{self.response["pagination"]["total"]}|{self.newest}'
        except KeyError:  # Failed request
            return

    @cached_property
    def property_name(self):
        return f'Floppy.Activity.{self.name}'

    @cached_property
    def value(self):
        return self.get_value()

    def get_value(self):
        from jurialmunkey.window import get_property
        from tmdbhelper.lib.addon.tmdate import get_timestring_zulu_now
        if not self.fingerprint:
            return
        previous = get_property(self.property_name)
        get_property(self.property_name, set_property=self.fingerprint)
        if previous and previous != self.fingerprint:
            return get_timestring_zulu_now()
        return self.newest


class FloppyLastActivities:
    """
    Floppy has no last activities endpoint so derive them from the newest entry of each list
    Keys match the MDbList sync/last_activities response used by SOURCE_ACTIVITIES
    """

    newest_kwgs = {'source': 'tmdb', 'sort': 'date_added', 'direction': 'desc'}

    def __init__(self, floppy_api):
        self.floppy_api = floppy_api

    def get_media_activity(self, name, media_type, status=None):
        return FloppyActivity(self.floppy_api, name, 'media', media_type, status=status, **self.newest_kwgs).value

    @cached_property
    def movie_watched_at(self):
        return self.get_media_activity('movie_watched', 'movie', FLOPPY_STATUS_COMPLETED)

    @cached_property
    def episode_watched_at(self):
        return self.get_media_activity('episode_watched', 'episode')

    @cached_property
    def movie_watchlisted_at(self):
        return self.get_media_activity('movie_watchlisted', 'movie', FLOPPY_STATUS_PLANNING)

    @cached_property
    def show_watchlisted_at(self):
        return self.get_media_activity('show_watchlisted', 'tv', FLOPPY_STATUS_PLANNING)

    @cached_property
    def show_dropped_at(self):
        return self.get_media_activity('show_dropped', 'tv', FLOPPY_STATUS_DROPPED)

    @cached_property
    def paused_at(self):
        return FloppyActivity(self.floppy_api, 'paused', 'playback', 'progress', key='updated_at').value

    @cached_property
    def any_activity_at(self):
        """ Watching an item changes its watchlist and dropped status so also resync those on any new activity """
        return max((i for i in (
            self.movie_watched_at,
            self.episode_watched_at,
            self.movie_watchlisted_at,
            self.show_watchlisted_at,
            self.show_dropped_at,
            self.paused_at,
        ) if i), default=None)

    @cached_property
    def data(self):
        if not self.any_activity_at:
            return {}
        return {
            'watched_at': self.movie_watched_at,
            'episode_watched_at': self.episode_watched_at,
            'paused_at': self.paused_at,
            'episode_paused_at': self.paused_at,
            'watchlisted_at': self.any_activity_at,
            'dropped_at': self.any_activity_at,
            'collected_at': None,
        }
