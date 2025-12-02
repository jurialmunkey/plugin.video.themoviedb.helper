import itertools
from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import ProgressDialog
from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.api.trakt.sync.datatype import (
    SyncWatched,
    SyncPlayback,
    SyncNextEpisodes,
    SyncAllNextEpisodes,
    SyncCollection,
    SyncWatchlist,
    SyncFavorites,
    SyncRatings,
    SyncHiddenProgressWatched,
    SyncHiddenProgressCollected,
    SyncHiddenCalendar,
    SyncHiddenDropped,
)


class SyncInvalidatorAll:

    notification = True
    localized_id = 593

    sync_table = {
        'plays': ('movie', 'show', ),
        'aired_episodes': ('show', ),
        'watched_episodes': ('show', ),
        'reset_at': ('movie', 'show', ),
        'last_watched_at': ('movie', 'show', ),
        'last_updated_at': ('movie', 'show', ),
        'rating': ('movie', 'show', ),
        'rated_at': ('movie', 'show', ),
        'favorites_rank': ('movie', 'show', ),
        'favorites_listed_at': ('movie', 'show', ),
        'favorites_notes': ('movie', 'show', ),
        'watchlist_rank': ('movie', 'show', 'season', 'episode', ),
        'watchlist_listed_at': ('movie', 'show', 'season', 'episode', ),
        'watchlist_notes': ('movie', 'show', 'season', 'episode', ),
        'collection_last_collected_at': ('movie', 'show', ),
        'collection_last_updated_at': ('movie', 'show', ),
        'playback_progress': ('movie', 'show', ),
        'playback_paused_at': ('movie', 'show', ),
        'playback_id': ('movie', 'show', ),
        'progress_watched_hidden_at': ('movie', 'show', ),
        'progress_collected_hidden_at': ('movie', 'show', ),
        'calendar_hidden_at': ('movie', 'show', ),
        'dropped_hidden_at': ('movie', 'show', ),
        'next_episode_id': ('show', ),
        'next_episode_aired_at': ('show', ),
        'upnext_episode_id': ('show', ),
    }

    # Define keys to resync
    sync_modes = (
        'plays',
        'aired_episodes',
        'watched_episodes',
        'reset_at',
        'last_watched_at',
        'last_updated_at',
        'rating',
        'rated_at',
        'favorites_rank',
        'favorites_listed_at',
        'favorites_notes',
        'watchlist_rank',
        'watchlist_listed_at',
        'watchlist_notes',
        'collection_last_collected_at',
        'collection_last_updated_at',
        'playback_progress',
        'playback_paused_at',
        'playback_id',
        'progress_watched_hidden_at',
        'progress_collected_hidden_at',
        'calendar_hidden_at',
        'dropped_hidden_at',
        'next_episode_id',
        'next_episode_aired_at',
        'upnext_episode_id',
    )

    @cached_property
    def name(self):
        return get_localized(self.localized_id)

    data = (
        SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes,
        SyncCollection, SyncWatchlist, SyncFavorites, SyncRatings,
        SyncHiddenProgressWatched, SyncHiddenProgressCollected,
        SyncHiddenCalendar, SyncHiddenDropped,
    )

    @cached_property
    def trakt_api(self):
        from tmdbhelper.lib.api.trakt.api import TraktAPI
        return TraktAPI()

    @cached_property
    def trakt_syncdata(self):
        return self.trakt_api.trakt_syncdata

    @cached_property
    def progress_dialog(self):
        if not self.notification:
            return
        return ProgressDialog(title=get_localized(32022), total=len(self.database_lactivities_ids) + 3)

    def progress_dialog_update(self, message):
        if not self.progress_dialog:
            return
        self.progress_dialog.update(message)

    def progress_dialog_close(self):
        if not self.progress_dialog:
            return
        self.progress_dialog.close()
        self.progress_dialog = None

    @cached_property
    def database(self):
        self.progress_dialog_update('Initialise database')
        return ItemDetailsDatabase()

    @staticmethod
    def data_build_keys(datatype):
        return tuple((
            f'{datatype.key_prefix}_{k}' if datatype.key_prefix else k
            for k in datatype.keys
        ))

    @cached_property
    def database_keys(self):
        database_keys = tuple((self.data_build_keys(i) for i in self.data))
        database_keys = tuple(itertools.chain.from_iterable(database_keys))
        return database_keys

    def database_del_column_data(self):
        self.progress_dialog_update(f'Deleting simplecache keys: {self.database_keys}')
        self.database.del_column_values(table='simplecache', keys=self.database_keys)

    @staticmethod
    def data_build_lactivities_ids(datatype, item_types=('movie', 'show', 'season', 'episode')):
        return tuple((f'{item_type}.{datatype.method}' for item_type in item_types))

    @cached_property
    def database_lactivities_ids(self):
        database_lactivities_ids = tuple((self.data_build_lactivities_ids(i) for i in self.data))
        database_lactivities_ids = tuple(itertools.chain.from_iterable(database_lactivities_ids))
        return database_lactivities_ids

    def database_del_lactivities(self):
        for item_id in self.database_lactivities_ids:
            self.progress_dialog_update(f'Deleting last activities keys: {item_id}')
            self.database.del_item(table='lactivities', item_id=item_id)

    def invalidate(self):
        self.database_del_column_data()
        self.database_del_lactivities()

    def sync_type(self, sync_type):
        sync_list = tuple((k for k, v in self.sync_table.items() if k in self.sync_modes and sync_type in v))
        self.trakt_syncdata.sync(sync_type, sync_list)

    def sync(self):
        self.sync_type('movie')
        self.sync_type('show')
        self.sync_type('season')
        self.sync_type('episode')

    def run(self, sync=False):
        self.invalidate()
        self.progress_dialog_close()
        self.sync() if sync else None
        if not self.notification:
            return
        Dialog().ok('Trakt', get_localized(32146 if sync else 32027).format(self.name.lower()))


class SyncInvalidatorWatchedProgress(SyncInvalidatorAll):
    data = (SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes)
    localized_id = 32035


class SyncInvalidatorCollection(SyncInvalidatorAll):
    data = (SyncCollection, )
    localized_id = 32192


class SyncInvalidatorWatchlist(SyncInvalidatorAll):
    data = (SyncWatchlist, )
    localized_id = 32193


class SyncInvalidatorFavorites(SyncInvalidatorAll):
    data = (SyncFavorites, )
    localized_id = 1036


class SyncInvalidatorRatings(SyncInvalidatorAll):
    data = (SyncRatings, )
    localized_id = 32028


class SyncInvalidatorHidden(SyncInvalidatorAll):
    data = (
        SyncHiddenProgressWatched, SyncHiddenProgressCollected,
        SyncHiddenCalendar, SyncHiddenDropped,
    )
    localized_id = 32036


def SyncInvalidator(datatype):
    routes = {
        'watchedprogress': SyncInvalidatorWatchedProgress,
        'collection': SyncInvalidatorCollection,
        'watchlist': SyncInvalidatorWatchlist,
        'favorites': SyncInvalidatorFavorites,
        'ratings': SyncInvalidatorRatings,
        'hidden': SyncInvalidatorHidden,
        'all': SyncInvalidatorAll,
    }

    try:
        route = routes[datatype]
    except KeyError:
        routes_list = [v for v in routes.values()]
        x = Dialog().select('Sync', [get_localized(i.localized_id) for i in routes_list])
        if x == -1:
            return
        route = routes_list[x]

    sync_invalidator = route()
    return sync_invalidator
