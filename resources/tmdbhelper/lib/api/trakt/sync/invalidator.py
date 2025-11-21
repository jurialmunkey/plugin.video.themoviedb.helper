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
    def progress_dialog(self):
        if not self.notification:
            return
        return ProgressDialog(title=get_localized(32022), total=4)

    def progress_dialog_update(self, message):
        if not self.progress_dialog:
            return
        self.progress_dialog.update(message)

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
    def data_build_lactivities_ids(datatype, item_types=('movie', 'show', 'episode')):
        return tuple((f'{item_type}.{datatype.method}' for item_type in item_types))

    @cached_property
    def database_lactivities_ids(self):
        database_lactivities_ids = tuple((self.data_build_lactivities_ids(i) for i in self.data))
        database_lactivities_ids = tuple(itertools.chain.from_iterable(database_lactivities_ids))
        return database_lactivities_ids

    def database_del_lactivities(self):
        self.progress_dialog.update(f'Deleting last activities keys: {self.database_lactivities_ids}')
        for item_id in self.database_lactivities_ids:
            self.database.del_item(table='lactivities', item_id=item_id)

    def invalidate(self):
        self.database_del_column_data()
        self.database_del_lactivities()

    def run(self, resync=False):
        self.invalidate()
        if not self.progress_dialog:
            return
        self.progress_dialog.close()
        self.progress_dialog = None
        Dialog().ok(
            get_localized(32026),
            get_localized(32027).format(self.name.lower())
        )


class SyncInvalidatorWatchedProgress(SyncInvalidatorAll):
    data = (SyncWatched, SyncPlayback, SyncNextEpisodes, SyncAllNextEpisodes)
    localized_id = 32035


class SyncInvalidatorCollection(SyncInvalidatorAll):
    data = (SyncCollection, ),
    localized_id = 32192


class SyncInvalidatorWatchlist(SyncInvalidatorAll):
    data = (SyncWatchlist, ),
    localized_id = 32193


class SyncInvalidatorFavorites(SyncInvalidatorAll):
    data = (SyncFavorites, ),
    localized_id = 1036


class SyncInvalidatorRatings(SyncInvalidatorAll):
    data = (SyncRatings, ),
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
