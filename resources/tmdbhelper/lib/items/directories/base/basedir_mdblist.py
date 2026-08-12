from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from tmdbhelper.lib.items.directories.base.item_builder_mdblist import BaseDirItemMDbListBuilder
from jurialmunkey.ftools import cached_property


class BaseDirItemMDbListTopLists(BaseDirItem):
    priority = 100
    label_localized = 32421
    label_type = 'localize'
    params = {'info': 'mdblist_toplists'}
    art_icon = 'resources/icons/mdblist/mdblist.png'
    types = ('both', )

    @property
    def enabled(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return bool(get_setting('mdblist_apikey', 'str'))


class BaseDirItemMDbListWatchlist(BaseDirItemMDbListTopLists):
    priority = 10
    label_type = 'suffixed'
    label_localized = 32193
    label_suffix = '(MDbList)'
    params = {'info': 'mdblist_watchlist'}
    sorting = True
    item_builder = BaseDirItemMDbListBuilder
    art_icon = 'resources/icons/sync/watchlist.png'
    types = ('movie', )
    group = 32193

    @cached_property
    def sort_label(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        return get_localized(32309)


class BaseDirItemMDbListWatchlistReleased(BaseDirItemMDbListWatchlist):
    priority = 20
    label_localized = 32456
    params = {'info': 'mdblist_watchlist_released'}


class BaseDirItemMDbListWatchlistAnticipated(BaseDirItemMDbListWatchlist):
    priority = 30
    label_localized = 32457
    params = {'info': 'mdblist_watchlist_anticipated'}


class BaseDirItemMDbListNextEpisodes(BaseDirItemMDbListTopLists):
    priority = 40
    label_type = 'suffixed'
    label_localized = 32197
    label_suffix = '(MDbList)'
    params = {'info': 'mdblist_nextepisodes'}
    art_icon = 'resources/icons/trakt/inprogress.png'
    types = ('tv', )
    group = 32196


class BaseDirItemMDbListYourLists(BaseDirItemMDbListTopLists):
    priority = 110
    label_localized = 32211
    params = {'info': 'mdblist_yourlists'}


class BaseDirItemMDbListSearchLists(BaseDirItemMDbListTopLists):
    priority = 120
    label_localized = 32361
    params = {'info': 'mdblist_searchlists'}


def get_all_mdblist_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
