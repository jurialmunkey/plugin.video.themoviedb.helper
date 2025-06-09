from tmdbhelper.lib.api.trakt.api import is_authorized
from tmdbhelper.lib.files.bcache import use_simple_cache


@is_authorized
def get_calendar(self, trakt_type, user=True, start_date=None, days=None, endpoint=None, **kwargs):
    user = 'my' if user else 'all'
    return self.get_response_json('calendars', user, trakt_type, endpoint, start_date, days, extended='full')


@use_simple_cache(cache_days=0.25)
def get_calendar_episodes(self, startdate=0, days=1, user=True, endpoint=None):
    # Broaden date range in case utc conversion bumps into different day
    from jurialmunkey.parser import try_int
    from tmdbhelper.lib.addon.tmdate import get_datetime_today, get_timedelta
    mod_date = try_int(startdate) - 1
    mod_days = try_int(days) + 2
    date = get_datetime_today() + get_timedelta(days=mod_date)
    return get_calendar(self, 'shows', user, start_date=date.strftime('%Y-%m-%d'), days=mod_days, endpoint=endpoint)
