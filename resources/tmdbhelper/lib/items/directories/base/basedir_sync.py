from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class BaseDirItemWatchlist(BaseDirItem):
    priority = 120
    label_type = 'reversed'
    label_localized = 32193
    types = ('movie', 'tv', 'season', 'episode', 'both', )
    params = {'info': 'trakt_watchlist'}
    sorting = True
    art_icon = 'resources/icons/sync/watchlist.png'
    group = 32193


class BaseDirItemTraktWatchListReleased(BaseDirItemWatchlist):
    priority = 130
    label_type = 'reversed'
    label_localized = 32456
    params = {'info': 'trakt_watchlist_released'}
    group = 32193


class BaseDirItemTraktWatchListAnticipated(BaseDirItemWatchlist):
    priority = 140
    label_type = 'reversed'
    label_localized = 32457
    params = {'info': 'trakt_watchlist_anticipated'}
    group = 32193


def get_all_sync_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
