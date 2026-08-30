from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import set_timestamp, get_timestamp, get_timestring_zulu_now
from tmdbhelper.lib.files.locker import mutexlock
from tmdbhelper.lib.addon.consts import DEFAULT_EXPIRY
from tmdbhelper.lib.sync.mixins import SyncDataParentProperties
from tmdbhelper.lib.sync.activity import SyncLastActivities


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
    lock_name = 'datasync'
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

    def get_response_sync_data(self, *args, **kwargs):
        return

    def get_response_sync(self, *args, **kwargs):
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
            get_timestring_zulu_now(),
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

    @cached_property
    def is_expired(self):
        return self.last_activities.is_expired(self.timestamp, keys=self.last_activities_keys)

    @cached_property
    def last_activity(self):
        return self.last_activities.get_last_activity(self.last_activities_keys)

    @cached_property
    def timestamp(self):
        return self.cache.get_activity(self.item_type, self.method, set_timestamp(0, set_int=True))

    @property
    def sync_args(self):
        return tuple()

    @timerlock
    def sync_func(self):
        from tmdbhelper.lib.addon.logger import TimerFunc
        with TimerFunc(f'Sync: {self.__class__.__name__} get_response_sync {self.method} {self.item_type}', inline=True, log_threshold=0.001):
            return self.get_response_sync(*self.sync_args, **self.sync_kwgs)

    def get_syncitem(self, meta):
        return

    @progress_bg
    def sync_data(self, **kwargs):
        self.dialog_progress_bg.update(20, message='Refreshing Data')
        meta = self.sync_func()

        # Failed sync returns None
        if meta is None:
            return False

        item = self.get_syncitem(meta)

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


class DataTypeEpisodesInShows:

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
