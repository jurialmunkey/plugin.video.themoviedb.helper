from tmdbhelper.lib.api.trakt.sync.property_mixins import SyncDataParentProperties
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp, convert_timestamp, is_unaired_timestamp
from tmdbhelper.lib.api.trakt.sync.activity import SyncLastActivities
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY, HALFDAY_EXPIRY


def timerlock(func):
    def wrapper(self, *args, **kwargs):
        interval = 3
        propname = f'syncdecorators.timerlock.sync_data'
        propname = f'{propname}.{self.item_type}.{self.method}'
        if get_timestamp(self.window.get_property(propname) or 0, set_int=True):
            return
        self.window.get_property(propname, set_timestamp(interval, set_int=True))
        data = func(self, *args, **kwargs)
        return data
    return wrapper


def progress_bg(func):
    def wrapper(self, *args, **kwargs):
        from tmdbhelper.lib.addon.dialog import DialogProgressSyncBG
        self.dialog_progress_bg = DialogProgressSyncBG()
        self.dialog_progress_bg.heading = f'Syncing {self.item_type} {self.method}'
        self.dialog_progress_bg.create()
        data = func(self, *args, **kwargs)
        self.dialog_progress_bg.close()
        return data
    return wrapper


class DataType(SyncDataParentProperties):
    sync_kwgs = {}
    lock_name = 'sync_trakt'
    key_prefix = None
    expiry_time = DEFAULT_EXPIRY

    def __init__(self, instance_syncdata, item_type):
        self.instance_syncdata = instance_syncdata
        self._item_type = item_type

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.{self.lock_name}.{self.item_type}.{self.method}.lockfile'

    @cached_property
    def item_type(self):
        if self._item_type in ('movie', 'show', 'season', 'episode'):
            return self._item_type
        raise ValueError(f'Invalid item_type {self._item_type} for {self.method}')

    def get_response_sync(self, *args, **kwargs):
        path = self.trakt_api.get_request_url(*args, **kwargs)
        data = self.trakt_api.get_api_request(path, headers=self.trakt_api.headers)
        if data is None:
            return
        try:
            return data.json()
        except ValueError:
            return
        except AttributeError:
            return

    @cached_property
    def last_activities(self):
        return self.get_last_activities()

    def get_last_activities(self):
        return SyncLastActivities(self.instance_syncdata)

    def store_last_activity(self):
        self.cache.set_activity(
            self.item_type,
            self.method,
            self.last_activities.json.get('all') or '2000-01-01T00:00:00.000Z',
            set_timestamp(self.expiry_time, set_int=True)
        )

    @property
    def last_activities_item_type(self):
        return f'{self.item_type}s'

    @property
    def last_activities_keys(self):
        return (self.last_activities_item_type, self.last_activities_key, )

    def clear_columns(self, keys):
        self.cache.del_column_values(keys=keys, item_type=self.item_type)
        self.clear_child_columns(keys)

    def clear_child_columns(self, keys):
        pass

    @property
    def is_expired(self):
        timestamp = self.cache.get_activity(self.item_type, self.method, set_timestamp(0, set_int=True))
        return self.last_activities.is_expired(timestamp, keys=self.last_activities_keys)

    @timerlock
    def sync_func(self):
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.__class__.__name__} get_response_sync {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync('sync', self.method, f'{self.item_type}s', **self.sync_kwgs)

    @progress_bg
    def sync_data(self, **kwargs):
        self.dialog_progress_bg.update(20, message='Refreshing Data')
        meta = self.sync_func()

        # Failed sync returns None
        if meta is None:
            return False

        from tmdbhelper.lib.api.trakt.sync.itemdata import SyncItem
        item = SyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

        self.dialog_progress_bg.update(40, message='Cleaning Data')
        self.clear_columns(item.base_table_keys)

        # Successful sync without items returns an empty list
        if not meta:
            return True

        self.dialog_progress_bg.update(60, message='Configuring Data')
        data = item.data

        self.dialog_progress_bg.update(80, message='Updating Data')
        self.cache.set_many_values(keys=item.table_keys, data=data)

        return True

    @mutexlock
    def sync(self, forced=False):
        if not forced and not self.is_expired:
            return
        if not self.sync_data():
            return
        self.store_last_activity()


class DataTypeEpisodes(DataType):

    @cached_property
    def item_type(self):
        if self._item_type in ('show', 'season', 'episode'):
            return 'show'
        if self._item_type == 'movie':
            return 'movie'
        raise ValueError(f'Invalid item_type {self._item_type} for {self.method}')

    def clear_child_columns(self, keys):
        if self.item_type == 'show':
            self.cache.del_column_values(keys=keys, item_type='season')
            self.cache.del_column_values(keys=keys, item_type='episode')

    @property
    def last_activities_item_type(self):
        if self.item_type == 'show':
            return 'episodes'
        return f'{self.item_type}s'


class SyncHiddenProgressWatched(DataType):
    keys = ('hidden_at', )
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_watched'
    key_prefix = 'progress_watched'

    @timerlock
    def sync_func(self):
        """ Get items that are hidden on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.__class__.__name__} get_response_sync users {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync('users', self.method, type=f'{self.item_type}s', limit=4095)


class SyncHiddenProgressCollected(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/progress_collected'
    key_prefix = 'progress_collected'


class SyncHiddenCalendar(SyncHiddenProgressWatched):
    last_activities_key = 'hidden_at'
    method = 'hidden/calendar'
    key_prefix = 'calendar'


class SyncHiddenDropped(SyncHiddenProgressWatched):
    last_activities_key = 'dropped_at'
    method = 'hidden/dropped'
    key_prefix = 'dropped'


class SyncWatched(DataTypeEpisodes):
    keys = ('plays', 'last_watched_at', 'last_updated_at', 'aired_episodes', 'watched_episodes', 'reset_at', )
    last_activities_key = 'watched_at'
    sync_kwgs = {'extended': 'full'}
    method = 'watched'


class SyncPlayback(DataTypeEpisodes):
    keys = ('progress', 'paused_at', 'id', )
    last_activities_key = 'paused_at'
    sync_kwgs = {'extended': 'full'}
    method = 'playback'
    key_prefix = 'playback'


class SyncRatings(DataType):
    keys = ('rating', 'rated_at', )
    last_activities_key = 'rated_at'
    method = 'ratings'


class SyncFavorites(DataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'favorited_at'
    sync_kwgs = {'extended': 'full'}
    method = 'favorites'
    key_prefix = 'favorites'


class SyncWatchlist(DataType):
    keys = ('rank', 'listed_at', 'notes', )
    last_activities_key = 'watchlisted_at'
    sync_kwgs = {'extended': 'full'}
    method = 'watchlist'
    key_prefix = 'watchlist'


class SyncCollection(DataTypeEpisodes):
    keys = ('last_collected_at', 'last_updated_at', )
    last_activities_key = 'collected_at'
    method = 'collection'
    key_prefix = 'collection'


class SyncNextEpisodeItem:
    def __init__(self, parent, item):
        self.parent = parent  # SyncAllNextEpisodes SyncNextEpisodes class
        self.item = item

    @cached_property
    def tmdb_id(self):
        try:
            return self.item['tmdb_id']
        except (KeyError, TypeError, NameError):
            return

    @cached_property
    def trakt_slug(self):
        try:
            return self.item['trakt_slug']
        except (KeyError, TypeError, NameError):
            return

    @property
    def get_response_sync(self):
        return self.parent.get_response_sync

    @cached_property
    def reset_at(self):
        return self.response.get('reset_at')

    @cached_property
    def reset_at_datetime_obj(self):
        if not self.reset_at:
            return
        return convert_timestamp(self.reset_at)

    @cached_property
    def next_episode(self):
        return self.response.get('next_episode')

    @cached_property
    def next_episode_aired_at(self):
        return self.next_episode['first_aired']

    @cached_property
    def next_episode_is_unaired(self):
        return is_unaired_timestamp(self.next_episode_aired_at)

    @cached_property
    def next_episode_season(self):
        return self.next_episode['season']

    @cached_property
    def next_episode_number(self):
        return self.next_episode['number']

    def get_next_episode_id(self, season, number):
        return f'tv.{self.tmdb_id}.{season}.{number}'

    def is_next_episode(self, episode):
        if not episode.get('completed'):
            return True
        if not self.reset_at_datetime_obj:
            return False
        if convert_timestamp(episode.get('last_watched_at')) < self.reset_at_datetime_obj:
            return True
        return False

    @cached_property
    def all_next_episodes(self):
        """
        Returns a generator of all next episodes by comparing againt reset_at date and timestamps
        """
        if not self.response:
            return

        return (
            self.get_next_episode_id(season['number'], episode['number'])
            for season in self.response_seasons for episode in (season.get('episodes') or [])
            if self.is_next_episode(episode)
        )

    @cached_property
    def response(self):
        if not self.trakt_slug:
            return
        return self.get_response_sync(
            f'shows/{self.trakt_slug}/progress/watched',
            extended='full')

    @cached_property
    def response_seasons(self):
        return self.response.get('seasons') or []

    @cached_property
    def next_episode_id(self):
        if not self.response:
            return
        if not self.reset_at and self.next_episode and not self.next_episode_is_unaired:
            return self.get_next_episode_id(self.next_episode_season, self.next_episode_number)
        try:
            return next(self.all_next_episodes)
        except StopIteration:
            return

    @cached_property
    def next_episode_id_dictionary(self):
        if not self.next_episode_id:
            return {}
        return {
            "next_episode_id": self.next_episode_id,
            "next_episode_aired_at": self.next_episode_aired_at,
            "show": {
                "ids": {
                    "tmdb": self.tmdb_id,
                    "slug": self.trakt_slug
                }
            }
        }


class SyncAllNextEpisodes(DataTypeEpisodes):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.logger import TimerFunc

        def get_item(i, item_id):
            tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
            return {
                "show": {
                    "ids": {
                        "tmdb": i["tmdb_id"],
                        "slug": i["trakt_slug"]
                    }
                },
                "upnext_episode_id": item_id,
                "type": "episode",
                "episode": {
                    "season": season_number,
                    "number": episode_number,
                }
            }

        def update_dialog_progress(sync):
            self.dialog_progress_bg.increment()
            self.dialog_progress_bg.set_message((
                f'Skip: {sync.tmdb_id} {sync.trakt_slug}'
                if not sync.all_next_episodes
                else f'Sync: {sync.tmdb_id} {sync.trakt_slug}'
            ))

        def get_items(i):
            sync = SyncNextEpisodeItem(self, i)
            update_dialog_progress(sync)
            return [get_item(i, item_id) for item_id in sync.all_next_episodes]

        def get_meta(sd):
            self.dialog_progress_bg.max_value = len(sd.items)
            with ParallelThread(sd.items, get_items) as pt:
                item_queue = pt.queue
            return [i for items in item_queue for i in items if i]

        def get_sd():
            sd = self.instance_syncdata.get_all_unhidden_shows_inprogress_getter()
            sd.additional_keys = ('trakt_slug', )
            return sd

        with TimerFunc(f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return get_meta(get_sd())


class SyncNextEpisodes(SyncAllNextEpisodes):
    keys = ('next_episode_id', 'next_episode_aired_at')
    last_activities_key = 'watched_at'
    method = 'nextup'
    expiry_time = HALFDAY_EXPIRY

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.logger import TimerFunc

        def update_dialog_progress(sync):
            self.dialog_progress_bg.increment()
            self.dialog_progress_bg.set_message((
                f'Skip: {sync.next_episode_id}'
                if not sync.next_episode_id
                else f'Sync: {sync.next_episode_id}'
            ))

        def get_item(i):
            sync = SyncNextEpisodeItem(self, i)
            update_dialog_progress(sync)
            return sync.next_episode_id_dictionary

        def get_meta(sd):
            self.dialog_progress_bg.max_value = len(sd.items)
            with ParallelThread(sd.items, get_item) as pt:
                item_queue = pt.queue
            return [i for i in item_queue if i]

        def get_sd():
            sd = self.instance_syncdata.get_all_unhidden_shows_inprogress_getter()
            sd.additional_keys = ('trakt_slug', )
            return sd

        with TimerFunc(f'Sync: {self.__class__.__name__} get_meta {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return get_meta(get_sd())
