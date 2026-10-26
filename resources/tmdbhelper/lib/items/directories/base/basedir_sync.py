from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItemAuthorised
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class BaseDirItemSync(BaseDirItemAuthorised):
    sync_capability = 'watched'

    @property
    def sync_capabilities(self):
        return (self.sync_capability,)

    @property
    def enabled(self):
        return any(not SyncProviderSetting(feature).is_never for feature in self.sync_capabilities)

    def get_authorisation(self):
        from tmdbhelper.lib.sync.auth import SyncProviderAuthorisation
        return SyncProviderAuthorisation(self.sync_capability)


class BaseDirItemCollection(BaseDirItemSync):
    priority = 100
    label_localized = 32192
    label_type = 'reversed'
    params = {'info': 'trakt_collection'}
    art_icon = '/resources/icons/sync/collection.png'
    sync_capability = 'collection'
    sorting = True
    types = ('movie', 'tv', 'both')
    group = 32192


class BaseDirItemWatchlist(BaseDirItemSync):
    sync_capability = 'watchlist'
    priority = 120
    label_type = 'reversed'
    label_localized = 32193
    types = ('movie', 'tv', 'season', 'episode', 'both', )
    params = {'info': 'trakt_watchlist'}
    sorting = True
    art_icon = 'resources/icons/sync/watchlist.png'
    group = 32193


class BaseDirItemWatchListReleased(BaseDirItemWatchlist):
    priority = 130
    label_type = 'reversed'
    label_localized = 32456
    params = {'info': 'trakt_watchlist_released'}
    group = 32193


class BaseDirItemWatchListAnticipated(BaseDirItemWatchlist):
    priority = 140
    label_type = 'reversed'
    label_localized = 32457
    params = {'info': 'trakt_watchlist_anticipated'}
    group = 32193


class BaseDirItemHistory(BaseDirItemSync):
    priority = 150
    label_localized = 32194
    sync_capability = 'watched'
    sorting = True
    types = ('movie', 'tv', 'episode', 'both', )
    params = {'info': 'trakt_history'}
    art_icon = 'resources/icons/sync/inprogress.png'
    group = 32194


class BaseDirItemOnDeckMovies(BaseDirItemSync):
    priority = 170
    label_localized = 32196
    types = ('movie', 'tv', )
    sync_capability = 'watched'
    params = {'info': 'trakt_inprogress'}
    sorting = True
    art_icon = 'resources/icons/sync/inprogress.png'
    group = 32196


class BaseDirItemOnDeckEpisodes(BaseDirItemOnDeckMovies):
    priority = 180
    label_type = 'localize'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'trakt_ondeck'}
    group = 32196


class BaseDirItemOnDeckUnWatchedMovie(BaseDirItemOnDeckMovies):
    priority = 190
    label_type = 'appended'
    label_localized = 32196
    types = ('movie', )
    params = {'info': 'trakt_ondeck_unwatched'}
    group = 32196

    @cached_property
    def label_append(self):
        return get_localized(16101)


class BaseDirItemToWatch(BaseDirItemSync):
    priority = 210
    label_type = 'reversed'
    label_localized = 32078
    types = ('movie', 'tv', )
    sync_capabilities = ('watched', 'watchlist')
    params = {'info': 'trakt_towatch'}
    art_icon = 'resources/icons/sync/watchlist.png'
    group = 32196


class BaseDirItemNextEpisodes(BaseDirItemOnDeckMovies):
    priority = 220
    label_type = 'localize'
    label_localized = 32197
    types = ('tv', )
    params = {'info': 'trakt_nextepisodes'}
    art_icon = 'resources/icons/sync/inprogress.png'
    group = 32196


class BaseDirItemOnDeckUnWatchedEpisodes(BaseDirItemOnDeckMovies):
    priority = 200
    label_type = 'suffixed'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'trakt_ondeck_unwatched'}
    group = 32196

    @cached_property
    def label_suffix(self):
        return f'({get_localized(16101)})'


def get_all_sync_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__) if clobj is not BaseDirItemSync]
