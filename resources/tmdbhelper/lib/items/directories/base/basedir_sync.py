from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItemAuthorised
from tmdbhelper.lib.items.directories.base.item_sync_builder import BaseDirSyncItemBuilder
from tmdbhelper.lib.items.directories.base.item_currentlywatching_builder import BaseDirCurrentlyWatchingItemBuilder
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.sync.providers.selection import SyncProviderSetting


class BaseDirItemSync(BaseDirItemAuthorised):
    sync_capability = 'watched'
    item_builder = BaseDirSyncItemBuilder

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
    params = {'info': 'sync_collection'}
    art_icon = 'resources/icons/sync/collection.png'
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
    params = {'info': 'sync_watchlist'}
    sorting = True
    art_icon = 'resources/icons/sync/watchlist.png'
    group = 32193


class BaseDirItemWatchListReleased(BaseDirItemWatchlist):
    priority = 130
    label_type = 'reversed'
    label_localized = 32456
    params = {'info': 'sync_watchlist_released'}
    art_icon = 'resources/icons/sync/watchlist-released.png'
    group = 32193


class BaseDirItemWatchListAnticipated(BaseDirItemWatchlist):
    priority = 140
    label_type = 'reversed'
    label_localized = 32457
    params = {'info': 'sync_watchlist_anticipated'}
    art_icon = 'resources/icons/sync/watchlist-anticipated.png'
    group = 32193


class BaseDirItemHistory(BaseDirItemSync):
    priority = 150
    label_localized = 32194
    sync_capability = 'watched'
    sorting = True
    types = ('movie', 'tv', 'episode', 'both', )
    params = {'info': 'sync_history'}
    art_icon = 'resources/icons/sync/recentlywatched.png'
    group = 32194


class BaseDirItemOnDeckMovies(BaseDirItemSync):
    priority = 170
    label_localized = 32196
    types = ('movie', 'tv', )
    sync_capability = 'watched'
    params = {'info': 'sync_inprogress'}
    sorting = True
    art_icon = 'resources/icons/sync/inprogress.png'
    group = 32196


class BaseDirItemOnDeckEpisodes(BaseDirItemOnDeckMovies):
    priority = 180
    label_type = 'localize'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'sync_ondeck'}
    group = 32196


class BaseDirItemOnDeckUnWatchedMovie(BaseDirItemOnDeckMovies):
    priority = 190
    label_type = 'appended'
    label_localized = 32196
    types = ('movie', )
    params = {'info': 'sync_ondeck_unwatched'}
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
    params = {'info': 'sync_towatch'}
    art_icon = 'resources/icons/sync/towatch.png'
    group = 32196


class BaseDirItemNextEpisodes(BaseDirItemOnDeckMovies):
    priority = 220
    label_type = 'localize'
    label_localized = 32197
    types = ('tv', )
    params = {'info': 'sync_nextepisodes'}
    art_icon = 'resources/icons/sync/up-next.png'
    group = 32196


class BaseDirItemCurrentlyWatching(BaseDirItemNextEpisodes):
    priority = 225
    label_type = 'standard'
    label_localized = 32600
    types = ('movie', 'tv', )
    params = {'info': 'sync_currentlywatching'}
    sorting = False
    art_icon = 'resources/icons/sync/currentlywatching.png'
    item_builder = BaseDirCurrentlyWatchingItemBuilder


class BaseDirItemNextMovies(BaseDirItemNextEpisodes):
    priority = 221
    label_localized = 32602
    types = ('movie', )
    params = {'info': 'sync_nextmovies'}
    sorting = False


class BaseDirItemCurrentlyWatchingMixed(BaseDirItemCurrentlyWatching):
    priority = 226
    types = ('both', )
    art_icon = 'resources/icons/sync/currentlywatching-both.png'


class BaseDirItemOnDeckUnWatchedEpisodes(BaseDirItemOnDeckMovies):
    priority = 200
    label_type = 'suffixed'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'sync_ondeck_unwatched'}
    group = 32196

    @cached_property
    def label_suffix(self):
        return f'({get_localized(16101)})'


class BaseDirItemMostWatched(BaseDirItemSync):
    sync_capability = 'watched'
    priority = 160
    label_localized = 32195
    types = ('movie', 'tv', 'episode', )
    params = {'info': 'sync_mostwatched'}
    art_icon = 'resources/icons/sync/mostwatched.png'
    group = 32195


class BaseDirItemDropped(BaseDirItemSync):
    sync_capability = 'watched'
    priority = 230
    label_type = 'localize'
    label_localized = 32048
    types = ('tv', )
    params = {'info': 'sync_dropped'}
    art_icon = 'resources/icons/sync/dropped.png'
    group = 32196


class BaseDirItemBecauseYouWatched(BaseDirItemSync):
    priority = 250
    label_localized = 32199
    types = ('movie', 'tv', )
    params = {'info': 'sync_becauseyouwatched'}
    art_icon = 'resources/icons/sync/recommended.png'
    group = 32223


class BaseDirItemBecauseMostWatched(BaseDirItemSync):
    priority = 260
    label_localized = 32200
    types = ('movie', 'tv', )
    params = {'info': 'sync_becausemostwatched'}
    art_icon = 'resources/icons/sync/recommended-mostwatched.png'
    group = 32223


class BaseDirItemAiringNext(BaseDirItemSync):
    priority = 280
    label_type = 'localize'
    label_localized = 32459
    types = ('tv', )
    params = {'info': 'sync_airingnext'}
    art_icon = 'resources/icons/sync/calendar.png'
    group = 32203


def get_all_sync_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__) if clobj is not BaseDirItemSync]
