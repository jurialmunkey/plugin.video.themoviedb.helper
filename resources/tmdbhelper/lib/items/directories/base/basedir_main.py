from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class BaseDirItemMainMovie(BaseDirItem):
    priority = 100
    label_localized = 342
    label_type = 'localize'
    params = {'info': 'dir_movie'}
    art_icon = 'resources/icons/themoviedb/movies.png'
    types = (None, )


class BaseDirItemMainTV(BaseDirItemMainMovie):
    priority = 110
    label_localized = 20343
    params = {'info': 'dir_tv'}
    art_icon = 'resources/icons/themoviedb/tv.png'


class BaseDirItemMainPerson(BaseDirItemMainMovie):
    priority = 120
    label_localized = 32172
    params = {'info': 'dir_person'}
    art_icon = 'resources/icons/themoviedb/cast.png'


class BaseDirItemMainMultiSearch(BaseDirItemMainMovie):
    priority = 130
    label_localized = 137
    params = {'info': 'dir_multisearch'}
    art_icon = 'resources/icons/themoviedb/search.png'


class BaseDirItemMainDiscover(BaseDirItemMainMovie):
    priority = 140
    label_localized = 32174
    params = {'info': 'dir_discover'}
    art_icon = 'resources/icons/themoviedb/discover.png'


class BaseDirItemMainRandom(BaseDirItemMainMovie):
    priority = 150
    label_localized = 32173
    params = {'info': 'dir_random'}
    art_icon = 'resources/icons/themoviedb/randomise.png'


class BaseDirItemMainTMDb(BaseDirItemMainMovie):
    priority = 160
    label = 'TheMovieDb'
    params = {'info': 'dir_tmdb'}
    art_icon = 'resources/icons/themoviedb/default.png'


class BaseDirItemMainTMDbv4(BaseDirItemMainMovie):
    priority = 170
    label = 'TMDb User'
    params = {'info': 'dir_tmdb_v4'}
    art_icon = 'resources/icons/themoviedb/default.png'


class BaseDirItemMainTrakt(BaseDirItemMainMovie):
    priority = 180
    label = 'Trakt'
    params = {'info': 'dir_trakt'}
    art_icon = 'resources/trakt.png'


class BaseDirItemMainTVDb(BaseDirItemMainMovie):
    priority = 190
    label = 'TVDb'
    params = {'info': 'dir_tvdb'}
    art_icon = 'resources/icons/tvdb/tvdb.png'


class BaseDirItemMainMDbList(BaseDirItemMainMovie):
    priority = 200
    label = 'MDbList'
    params = {'info': 'dir_mdblist'}
    art_icon = 'resources/icons/mdblist/mdblist.png'


class BaseDirItemMain(BaseDirItemMainMovie):
    priority = 210
    label = 'Nodes'
    params = {'info': 'dir_custom_node'}
    art_icon = 'resources/icons/themoviedb/default.png'


class BaseDirItemMainSettings(BaseDirItemMainMovie):
    priority = 220
    label_localized = 5
    params = {'info': 'dir_settings'}
    art_icon = 'resources/icons/themoviedb/settings.png'


def get_all_main_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
