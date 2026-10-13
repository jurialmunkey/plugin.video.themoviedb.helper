from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.mdblist.dataconf import configure_episode_list, configure_episode_snapshot
from tmdbhelper.lib.sync.mdblist.datatype import MDbListDataType, MDbListDataTypeEpisodesToShows, MDbListDataTypeSnapshot
from tmdbhelper.lib.sync.mdblist.pagination import MDbListSyncCollection


class MDbListWatchedCollection:

    def __init__(self, instance_datatype, *args, **kwargs):
        self.instance_datatype = instance_datatype
        self.args = args
        self.kwargs = kwargs

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        return self.get_raw_data()

    def get_raw_data(self):
        return MDbListSyncCollection(self.instance_datatype, *self.args, **self.kwargs).data


class MDbListWatchedCollectionEpisodes(MDbListWatchedCollection):

    def get_data(self):
        data = self.get_raw_data()
        return configure_episode_list(data) if data else data


class MDbListWatchedSnapshotEpisodes(MDbListWatchedCollectionEpisodes):

    def get_raw_data(self):
        data = self.get_episode_snapshot()
        return data if data is not None else self.get_full_episodes()

    @cached_property
    def episodes(self):
        return self.get_episodes()

    def get_episodes(self):
        return self.get_snapshot('episode', **dict(self.kwargs, extended='ids_only'))

    @cached_property
    def shows(self):
        return self.get_shows()

    def get_shows(self):
        return self.get_snapshot('show', **self.kwargs)

    def get_snapshot(self, item_type, **kwargs):
        snapshot = MDbListDataTypeSnapshot(self.instance_datatype.instance_syncdata, item_type)
        snapshot.dialog_progress_bg = self.instance_datatype.dialog_progress_bg
        kwargs['mediatype'] = item_type
        return snapshot.get_response_sync(*self.args, **kwargs)

    def get_episode_snapshot(self):
        if self.episodes == []:
            return self.episodes
        if self.episodes is None or self.shows is None:
            return
        return configure_episode_snapshot(self.episodes, self.shows)

    def get_full_episodes(self):
        from tmdbhelper.lib.addon.logger import kodi_log
        kodi_log('Sync: falling back to full MDbList watched episode responses', 2)
        return self.get_snapshot('episode', **self.kwargs)


def MDbListWatchedCollectionFactory(instance_datatype, *args, **kwargs):
    routes = {
        ('movie', False): MDbListWatchedCollection,
        ('movie', True): MDbListWatchedCollection,
        ('episode', False): MDbListWatchedSnapshotEpisodes,
        ('episode', True): MDbListWatchedCollectionEpisodes,
    }
    collection_class = routes[(instance_datatype.sync_kwgs_mediatype, bool(instance_datatype.timestamp))]
    return collection_class(instance_datatype, *args, **kwargs)


class SyncWatched(MDbListDataType):
    keys = ('plays', 'last_watched_at', )
    last_activities_key = 'watched_at'
    method = 'sync/watched'

    def get_data_list_by_type(self, data):
        try:
            return data[f'{self.sync_kwgs_mediatype}s']
        except KeyError:
            return

    def get_response_sync_list(self, *args, **kwargs):
        return MDbListWatchedCollectionFactory(self, *args, **kwargs).data

    def clear_columns(self, *args, **kwargs):
        if self.timestamp:  # Skip clearing columns if we just update
            return
        super().clear_columns(*args, **kwargs)

    @property
    def sync_kwgs(self):
        sync_kwgs = (
            ('mediatype', self.sync_kwgs_mediatype),
            ('since', self.timestamp),  # TODO: DO THIS WITH JOURNAL INSTEAD AND REMOVE ITEMS too
        )
        return {k: v for k, v in sync_kwgs if v}


class SyncWatchedMovies(SyncWatched):
    sync_kwgs_mediatype = 'movie'


class SyncWatchedEpisodes(MDbListDataTypeEpisodesToShows, SyncWatched):
    sync_kwgs_mediatype = 'episode'


class SyncWatchedFactory(SyncWatched):

    def __new__(cls, instance_syncdata, item_type):
        routes = {
            'movie': SyncWatchedMovies,
            'show': SyncWatchedEpisodes,
            'season': SyncWatchedEpisodes,
            'episode': SyncWatchedEpisodes,
        }
        return routes[item_type](instance_syncdata, item_type)
