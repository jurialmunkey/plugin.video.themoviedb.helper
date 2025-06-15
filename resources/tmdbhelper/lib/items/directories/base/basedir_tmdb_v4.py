from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class BaseDirItemTMDbv4Recommendations(BaseDirItem):
    priority = 100
    label_localized = 32223
    params = {'info': 'tmdb_v4_recommendations'}
    art_icon = 'resources/icons/themoviedb/popular.png'
    types = ('movie', 'tv', )


class BaseDirItemTMDbv4Favorites(BaseDirItemTMDbv4Recommendations):
    priority = 100
    label_localized = 1036
    params = {'info': 'tmdb_v4_favorites'}
    art_icon = 'resources/icons/themoviedb/recommended.png'
    types = ('movie', 'tv', )


class BaseDirItemTMDbv4Rated(BaseDirItemTMDbv4Recommendations):
    priority = 100
    label_localized = 32521
    params = {'info': 'tmdb_v4_rated'}
    art_icon = 'resources/icons/themoviedb/tags.png'
    types = ('movie', 'tv', )


class BaseDirItemTMDbv4Watchlist(BaseDirItemTMDbv4Recommendations):
    priority = 100
    label_localized = 32193
    params = {'info': 'tmdb_v4_watchlist'}
    art_icon = 'resources/icons/themoviedb/similar.png'
    types = ('movie', 'tv', )


class BaseDirItemTMDbv4Lists(BaseDirItemTMDbv4Recommendations):
    priority = 100
    label_localized = 32211
    params = {'info': 'tmdb_v4_lists'}
    art_icon = 'resources/icons/themoviedb/reviews.png'
    types = ('both', )


def get_all_tmdb_v4_class_instances():
    from tmdbhelper.lib.api.tmdb.users import TMDbUser
    if not TMDbUser().authenticator.authorised_access:
        return []
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
