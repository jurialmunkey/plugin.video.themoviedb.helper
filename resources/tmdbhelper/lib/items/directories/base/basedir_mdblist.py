from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class BaseDirItemMDbListTopLists(BaseDirItem):
    priority = 100
    label_localized = 32421
    label_type = 'localize'
    params = {'info': 'mdblist_toplists'}
    art_icon = 'resources/icons/mdblist/toplists.png'
    types = ('both', )

    @property
    def enabled(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return bool(get_setting('mdblist_apikey', 'str'))


class BaseDirItemMDbListCuratedLists(BaseDirItemMDbListTopLists):
    priority = 102
    label_localized = 32543
    params = {'info': 'mdblist_curatedlists'}
    art_icon = 'resources/icons/mdblist/curatedlists.png'


class BaseDirItemMDbListOfficialLists(BaseDirItemMDbListTopLists):
    priority = 104
    label_localized = 32544
    label_type = 'standard'
    params = {'info': 'mdblist_officiallists'}
    art_icon = 'resources/icons/mdblist/officiallists.png'
    types = ('movie', 'tv', )


class BaseDirItemMDbListStreamingCharts(BaseDirItemMDbListTopLists):
    priority = 106
    label_localized = 32545
    label_type = 'standard'
    params = {'info': 'mdblist_streamingcharts'}
    art_icon = 'resources/icons/mdblist/streamingcharts.png'
    types = ('movie', 'tv', )


class BaseDirItemMDbListLikedLists(BaseDirItemMDbListTopLists):
    priority = 108
    label_localized = 32210
    params = {'info': 'mdblist_likedlists'}
    art_icon = 'resources/icons/mdblist/likedlists.png'


class BaseDirItemMDbListYourLists(BaseDirItemMDbListTopLists):
    priority = 110
    label_localized = 32211
    params = {'info': 'mdblist_yourlists'}
    art_icon = 'resources/icons/mdblist/yourlists.png'


class BaseDirItemMDbListSearchLists(BaseDirItemMDbListTopLists):
    priority = 120
    label_localized = 32361
    params = {'info': 'mdblist_searchlists'}
    art_icon = 'resources/icons/mdblist/searchlists.png'


def get_all_mdblist_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
