from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem


class TMDbDirectoryItem(BaseDirItem):
    priority = 170
    label = 'TMDb'
    params = {'info': 'tmdb_directory'}
    art_icon = 'resources/icons/themoviedb/user.png'
    types = ('both',)


class TMDbRecommendationsItem(BaseDirItem):
    label_localized = 32223
    params = {'info': 'tmdb_recommendations'}
    art_icon = 'resources/icons/themoviedb/recommended.png'
    types = ('movie', 'tv')


class TMDbFavoritesItem(TMDbRecommendationsItem):
    label_localized = 1036
    params = {'info': 'tmdb_favorites'}
    art_icon = 'resources/icons/themoviedb/favorites.png'


class TMDbRatedItem(TMDbRecommendationsItem):
    label_localized = 32521
    params = {'info': 'tmdb_rated'}
    art_icon = 'resources/icons/themoviedb/rated.png'


class TMDbListsItem(TMDbRecommendationsItem):
    label_localized = 32211
    params = {'info': 'tmdb_lists'}
    art_icon = 'resources/icons/themoviedb/lists.png'
    types = ('both',)


def get_menu_items():
    return [item_class() for item_class in (
        TMDbRecommendationsItem, TMDbFavoritesItem, TMDbRatedItem, TMDbListsItem)]
