from tmdbhelper.lib.files.futils import get_json_filecache, set_json_filecache
from tmdbhelper.lib.addon.tmdate import is_future_timestamp, get_todays_date
from jurialmunkey.ftools import cached_property


class LibraryUpdateTvshowCacher():
    """ Class used for caching tvshow library update actions
    Arguments
    tmdb_id -- tmdb_id of the tvshow
    """

    cache_version = 4
    forced = False

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

    @cached_property
    def cache_name(self):
        return f'library_autoupdate_tv.{self.tmdb_id}'

    @cached_property
    def cache_info(self):
        if self.forced:
            return {}
        cache_info = get_json_filecache(self.cache_name) or {}
        if cache_info.get('version') != self.cache_version:
            return {}
        return cache_info

    @cached_property
    def my_history(self):
        return {}

    def set_cache(self, cache_days=120):
        set_json_filecache(self.my_history, self.cache_name, cache_days=cache_days)

    @cached_property
    def next_check(self):
        try:
            next_check = self.cache_info['next_check']
        except KeyError:
            return
        if not next_check:
            return
        if not is_future_timestamp(next_check, "%Y-%m-%d", 10):
            return
        return f'{self.cache_info.get("log_msg")} next update {next_check}'

    def make_new_cache(self, name):
        today_date = get_todays_date()
        self.my_history = {
            'version': self.cache_version,
            'name': name,
            'next_check': today_date,
            'last_check': today_date,
            'log_msg': ''}

    def set_next_check(self, next_aired, last_aired, status):
        """ Set the next check date for this show based on next/last aired and status """
        if next_aired and next_aired.get('air_date'):
            next_aired_dt = next_aired.get('air_date')
            if is_future_timestamp(next_aired_dt, "%Y-%m-%d", 10):
                if not is_future_timestamp(next_aired_dt, "%Y-%m-%d", 10, days=7):
                    self.my_history['next_check'] = next_aired.get('air_date')
                    self.my_history['log_msg'] = 'Show had next aired date this week'
                    # Check again on the next aired date
                elif not is_future_timestamp(next_aired_dt, "%Y-%m-%d", 10, days=30):
                    self.my_history['next_check'] = get_todays_date(days=7)
                    self.my_history['log_msg'] = 'Show has next aired date this month'
                    # Check again in a week just to be safe in case air date changes
                else:
                    self.my_history['next_check'] = get_todays_date(days=30)
                    self.my_history['log_msg'] = 'Show has next aired date in more than a month'
                    # Check again in a month just to be safe in case air date changes
            else:
                next_aired = None  # Next aired was in the past for some reason so dont use that date

        if not next_aired and last_aired and last_aired.get('air_date'):
            last_aired_dt = last_aired.get('air_date')
            if is_future_timestamp(last_aired_dt, "%Y-%m-%d", 10, days=-30):
                self.my_history['next_check'] = get_todays_date(days=1)
                self.my_history['log_msg'] = 'Show aired in last month but no next aired date'
                # Show might be currently airing but just hasnt updated next date yet so check again tomorrow
            elif is_future_timestamp(last_aired_dt, "%Y-%m-%d", 10, days=-90):
                self.my_history['log_msg'] = 'Show aired in last quarter but not in last month'
                self.my_history['next_check'] = get_todays_date(days=7)
                # Show might be on a mid-season break so check again in a week for a return date
            elif status in ['Canceled', 'Ended']:
                self.my_history['log_msg'] = 'Show was canceled or ended'
                self.my_history['next_check'] = get_todays_date(days=30)
                # Show was canceled so check again in a month just to be safe
            else:
                self.my_history['log_msg'] = 'Show last aired more than 3 months ago and no next aired date set'
                self.my_history['next_check'] = get_todays_date(days=7)
                # Show hasnt aired in a while so check every week for a return date
