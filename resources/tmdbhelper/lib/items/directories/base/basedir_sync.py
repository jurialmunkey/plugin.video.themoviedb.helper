from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItemAuthorised
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class BaseDirItemCollection(BaseDirItemAuthorised):
    priority = 100
    label_localized = 32192
    label_type = 'reversed'
    params = {'info': 'trakt_collection'}
    art_icon = '/resources/icons/sync/collection.png'
    authorisation_setting = 'sync_source_collection'
    sorting = True
    types = ('movie', 'tv', 'both')
    group = 32192


class BaseDirItemWatchlist(BaseDirItemAuthorised):
    priority = 120
    label_type = 'reversed'
    label_localized = 32193
    authorisation_setting = 'sync_source_watchlist'
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


class BaseDirItemHistory(BaseDirItemAuthorised):
    priority = 150
    label_localized = 32194
    authorisation_setting = 'sync_source_watched'
    sorting = True
    types = ('movie', 'tv', 'episode', 'both', )
    params = {'info': 'trakt_history'}
    art_icon = 'resources/icons/sync/inprogress.png'
    group = 32194


class BaseDirItemOnDeckMovies(BaseDirItemAuthorised):
    priority = 170
    label_localized = 32196
    # types = ('movie', 'tv', )
    authorisation_setting = 'sync_source_watched'
    types = ('movie', )  # TODO: ADD TV SHOW IN PROGRESS
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
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
