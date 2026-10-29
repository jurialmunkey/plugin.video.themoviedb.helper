from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property


class BaseDirItemRandomGenres(BaseDirItem):
    priority = 100
    label_prefix = 590
    label_suffix = 515
    params = {'info': 'random_genres'}
    art_icon = 'resources/icons/themoviedb/genre.png'
    types = ('movie', 'tv', )

    @cached_property
    def label(self):
        return '{label_prefix}{{space}}{{item_type}} {label_suffix}'.format(
            label_prefix=get_localized(self.label_prefix),
            label_suffix=get_localized(self.label_suffix)
        )


class BaseDirItemRandomProviders(BaseDirItemRandomGenres):
    priority = 110
    label_suffix = 32411
    params = {'info': 'random_providers'}
    art_icon = 'resources/icons/themoviedb/providers.png'


class BaseDirItemRandomKeywords(BaseDirItemRandomGenres):
    priority = 120
    label_suffix = 32117
    params = {'info': 'random_keywords'}
    art_icon = 'resources/icons/themoviedb/tags.png'
    types = ('movie', )


class BaseDirItemRandomNetworks(BaseDirItemRandomGenres):
    priority = 130
    label_suffix = 705
    params = {'info': 'random_networks'}
    art_icon = 'resources/icons/themoviedb/networks.png'
    types = ('tv', )


class BaseDirItemRandomStudios(BaseDirItemRandomGenres):
    priority = 140
    label_suffix = 572
    params = {'info': 'random_studios'}
    art_icon = 'resources/icons/themoviedb/studios.png'
    types = ('movie', )


class BaseDirItemRandomBecauseYouWatched(BaseDirItemRandomGenres):
    priority = 150
    label_prefix = 32199
    params = {'info': 'sync_becauseyouwatched'}
    art_icon = 'resources/icons/sync/recommended.png'
    types = ('movie', 'tv', )

    @cached_property
    def label(self):
        return '{label_prefix}{{space}}{{item_type}}'.format(
            label_prefix=get_localized(self.label_prefix),
        )


class BaseDirItemRandomBecauseMostWatched(BaseDirItemRandomBecauseYouWatched):
    priority = 160
    label_suffix = 32200
    params = {'info': 'sync_becausemostwatched'}
    art_icon = 'resources/icons/sync/recommended-mostwatched.png'


def get_all_random_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
