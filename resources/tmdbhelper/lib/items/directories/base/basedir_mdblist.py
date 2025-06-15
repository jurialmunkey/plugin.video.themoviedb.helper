from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class BaseDirItemMDbListTopLists(BaseDirItem):
    priority = 100
    label_localized = 32421
    label_type = 'localize'
    params = {'info': 'mdblist_toplists'}
    art_icon = 'resources/icons/mdblist/mdblist.png'
    types = ('both', )


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
