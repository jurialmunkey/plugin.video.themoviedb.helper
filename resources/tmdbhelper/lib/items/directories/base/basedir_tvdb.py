from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from tmdbhelper.lib.addon.consts import TVDB_DISCLAIMER


class BaseDirItemTVDbAwards(BaseDirItem):
    priority = 100
    label_localized = 32460
    label_type = 'localize'
    params = {'info': 'dir_tvdb_awards'}
    infolabels = {'plot': TVDB_DISCLAIMER}
    art_icon = 'resources/icons/tvdb/tvdb.png'
    types = ('both', )


class BaseDirItemTVDbGenres(BaseDirItem):
    priority = 200
    label_localized = 135
    label_type = 'reversed'
    params = {'info': 'dir_tvdb_genres'}
    infolabels = {'plot': TVDB_DISCLAIMER}
    art_icon = 'resources/icons/tvdb/tvdb.png'
    types = ('both', )


def get_all_tvdb_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
