from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp
from tmdbhelper.lib.api.trakt.sync.activity import SyncLastActivities
from tmdbhelper.lib.files.locker import mutexlock


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


class DataType:
    sync_kwgs = {}
    lock_name = 'sync_trakt'
    key_prefix = None

    def __init__(self, class_instance_syncdata, item_type):
        self._class_instance_syncdata = class_instance_syncdata
        self._item_type = item_type

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.{self.lock_name}.{self.item_type}.{self.method}.lockfile'

    @property
    def cache(self):
        return self._class_instance_syncdata.cache

    @property
    def window(self):
        return self._class_instance_syncdata.window

    @property
    def item_type(self):
        return self._item_type

    @property
    def get_response_json(self):
        return self._class_instance_syncdata.get_response_json

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

    @property
    def trakt_api(self):
        return self._class_instance_syncdata._class_instance_trakt_api

    @cached_property
    def last_activities(self):
        return self.get_last_activities()

    def get_last_activities(self):
        return SyncLastActivities(self._class_instance_syncdata)

    def store_last_activity(self):
        self.cache.set_activity(self.item_type, self.method, self.last_activities.json.get('all') or '2000-01-01T00:00:00.000Z')

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
        timestamp = self.cache.get_activity(self.item_type, self.method)
        return self.last_activities.is_expired(timestamp, keys=self.last_activities_keys)

    @timerlock
    def sync_func(self):
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync('sync', self.method, f'{self.item_type}s', **self.sync_kwgs)

    @progress_bg
    def sync_data(self, **kwargs):
        self.dialog_progress_bg.update(20, message='Refreshing Data')
        meta = self.sync_func()
        if meta is None:
            return

        from tmdbhelper.lib.api.trakt.sync.itemdata import SyncItem
        item = SyncItem(self.item_type, meta, self.keys, key_prefix=self.key_prefix)

        self.dialog_progress_bg.update(40, message='Cleaning Data')
        self.clear_columns(item.base_table_keys)

        if not meta:
            return

        self.dialog_progress_bg.update(60, message='Configuring Data')
        data = item.data

        self.dialog_progress_bg.update(80, message='Updating Data')
        self.cache.set_many_values(keys=item.table_keys, data=data)

        return (item.table_keys, data, )

    @mutexlock
    def sync(self, forced=False):
        if not forced and not self.is_expired:
            return
        self.store_last_activity()
        self.sync_data()


class DataTypeEpisodes(DataType):
    def clear_child_columns(self, keys):
        if self.item_type == 'show':
            self.cache.del_column_values(keys=keys, item_type='season')
            self.cache.del_column_values(keys=keys, item_type='episode')

    @property
    def last_activities_item_type(self):
        if self.item_type == 'show':
            return 'episodes'
        return f'{self.item_type}s'


class SyncHidden(DataType):
    keys = ('hidden_at', )
    last_activities_key = 'hidden_at'
    method = 'hidden'

    @timerlock
    def sync_func(self):
        """ Get items that are hidden on Trakt """
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            response = []
            response += self.get_response_sync('users', self.method, 'progress_watched', type=f'{self.item_type}s', limit=4095) or []
            response += self.get_response_sync('users', self.method, 'progress_collected', type=f'{self.item_type}s', limit=4095) or []
            response += self.get_response_sync('users', self.method, 'calendar', type=f'{self.item_type}s', limit=4095) or []
            return response


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


class SyncAllNextEpisodes(DataTypeEpisodes):
    keys = ('upnext_episode_id', )
    last_activities_key = 'watched_at'
    method = 'all_next_episodes'

    def get_all_next_episodes(self, response, tmdb_id):
        # For list of episodes we need to build them by comparing against the reset_at date
        from tmdbhelper.lib.addon.tmdate import convert_timestamp
        reset_at = convert_timestamp(response['reset_at']) if response.get('reset_at') else None
        return (
            f'tv.{tmdb_id}.{season["number"]}.{episode["number"]}'
            for season in response.get('seasons', []) for episode in season.get('episodes', [])
            if not episode.get('completed') or (reset_at and convert_timestamp(episode.get('last_watched_at')) < reset_at))

    def get_next_episodes_response(self, trakt_id):
        if not trakt_id:
            return
        return self.get_response_sync('shows', trakt_id, 'progress/watched')

    def get_next_episodes(self, tmdb_id, trakt_id):
        response = self.get_next_episodes_response(trakt_id)
        if not response:
            return
        return self.get_all_next_episodes(response, tmdb_id)

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.logger import TimerFunc

        dpro = self.dialog_progress_bg

        def get_item(i, item_id):
            tmdb_type, tmdb_id, season_number, episode_number = item_id.split('.')
            item = {"show": {"ids": {"tmdb": i["tmdb_id"], "trakt": i["trakt_id"]}}}
            item['upnext_episode_id'] = item_id
            item['type'] = 'episode'
            item['episode'] = {'season': season_number, 'number': episode_number}
            return item

        def get_items(i):
            next_episodes = self.get_next_episodes(i["tmdb_id"], i["trakt_id"])
            dpro.increment()
            if not next_episodes:
                dpro.set_message(f'Skip: {i["tmdb_id"]} {i["trakt_id"]}')
                return
            dpro.set_message(f'Sync: {i["tmdb_id"]} {i["trakt_id"]}')
            return [get_item(i, item_id) for item_id in next_episodes]

        with TimerFunc(f'Sync: {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            sd = self._class_instance_syncdata.get_all_unhidden_shows_inprogress_getter()
            sd.additional_keys = ('trakt_id', )
            dpro.max_value = len(sd.items)
            with ParallelThread(sd.items, get_items) as pt:
                item_queue = pt.queue
            meta = [i for items in item_queue for i in items if i]
        return meta


class SyncNextEpisodes(SyncAllNextEpisodes):
    keys = ('next_episode_id', )
    last_activities_key = 'watched_at'
    method = 'nextup'

    def get_next_episode(self, tmdb_id, trakt_id):
        response = self.get_next_episodes_response(trakt_id)
        if not response:
            return
        if not response.get('reset_at') and response.get('next_episode'):
            return f'tv.{tmdb_id}.{response["next_episode"]["season"]}.{response["next_episode"]["number"]}'

        # Get a next item generator to only check for one next episode not all
        items = self.get_all_next_episodes(response, tmdb_id)
        try:
            return next(items)
        except StopIteration:
            return

    @timerlock
    def sync_func(self):
        """ Get next episodes on Trakt """
        from tmdbhelper.lib.addon.thread import ParallelThread
        from tmdbhelper.lib.addon.logger import TimerFunc

        dpro = self.dialog_progress_bg

        def get_item(i):
            next_episode_id = self.get_next_episode(i["tmdb_id"], i["trakt_id"])
            dpro.increment()
            if not next_episode_id:
                dpro.set_message(f'Skip: {next_episode_id}')
                return
            dpro.set_message(f'Sync: {next_episode_id}')
            return {"next_episode_id": next_episode_id, "show": {"ids": {"tmdb": i["tmdb_id"], "trakt": i["trakt_id"]}}}

        with TimerFunc(f'Sync: {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            sd = self._class_instance_syncdata.get_all_unhidden_shows_inprogress_getter()
            sd.additional_keys = ('trakt_id', )
            dpro.max_value = len(sd.items)
            with ParallelThread(sd.items, get_item) as pt:
                item_queue = pt.queue
            meta = [i for i in item_queue if i]
        return meta
