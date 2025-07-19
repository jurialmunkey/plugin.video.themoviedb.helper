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
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemRandomKeywords(BaseDirItemRandomGenres):
    priority = 120
    label_suffix = 32117
    params = {'info': 'random_keywords'}
    art_icon = 'resources/icons/themoviedb/default.png'
    types = ('movie', )


class BaseDirItemRandomNetworks(BaseDirItemRandomGenres):
    priority = 130
    label_suffix = 705
    params = {'info': 'random_networks'}
    art_icon = 'resources/icons/themoviedb/default.png'
    types = ('tv', )


class BaseDirItemRandomStudios(BaseDirItemRandomGenres):
    priority = 140
    label_suffix = 572
    params = {'info': 'random_studios'}
    art_icon = 'resources/icons/themoviedb/default.png'
    types = ('movie', )


class BaseDirItemRandomBecauseYouWatched(BaseDirItemRandomGenres):
    priority = 150
    label_prefix = 32199
    params = {'info': 'trakt_becauseyouwatched'}
    art_icon = 'resources/icons/trakt/recommended.png'
    types = ('movie', 'tv', )

    @cached_property
    def label(self):
        return '{label_prefix}{{space}}{{item_type}}'.format(
            label_prefix=get_localized(self.label_prefix),
        )


class BaseDirItemRandomBecauseMostWatched(BaseDirItemRandomBecauseYouWatched):
    priority = 160
    label_suffix = 32200
    params = {'info': 'trakt_becausemostwatched'}


class BaseDirItemRandomTrending(BaseDirItem):
    priority = 170
    label_prefix = 32204
    label_append = 590
    params = {'info': 'random_trending'}
    types = ('movie', 'tv', 'both', )
    art_icon = 'resources/icons/trakt/trend.png'

    @cached_property
    def label(self):
        return '{label_append} {label_prefix}{{space}}{{item_type}}'.format(
            label_prefix=get_localized(self.label_prefix),
            label_append=get_localized(self.label_append)
        )


class BaseDirItemRandomPopular(BaseDirItemRandomTrending):
    priority = 180
    label_prefix = 32175
    params = {'info': 'random_popular'}
    art_icon = 'resources/icons/trakt/popular.png'


class BaseDirItemRandomMostPlayed(BaseDirItemRandomTrending):
    priority = 190
    label_prefix = 32205
    params = {'info': 'random_mostplayed'}
    art_icon = 'resources/icons/trakt/mostplayed.png'


class BaseDirItemRandomMostViewers(BaseDirItemRandomTrending):
    priority = 200
    label_prefix = 32414
    params = {'info': 'random_mostviewers'}
    art_icon = 'resources/icons/trakt/mostplayed.png'


class BaseDirItemRandomAnticipated(BaseDirItemRandomTrending):
    priority = 210
    label_prefix = 32206
    params = {'info': 'random_anticipated'}
    art_icon = 'resources/icons/trakt/anticipated.png'


class BaseDirItemRandomTrendingLists(BaseDirItemRandomTrending):
    priority = 220
    label_prefix = 32300
    params = {'info': 'random_trendinglists'}
    art_icon = 'resources/icons/trakt/trendinglist.png'
    types = ('both', )


class BaseDirItemRandomPopularLists(BaseDirItemRandomTrending):
    priority = 230
    label_prefix = 32301
    params = {'info': 'random_popularlists'}
    art_icon = 'resources/icons/trakt/popularlist.png'
    types = ('both', )


class BaseDirItemRandomLikedLists(BaseDirItemRandomTrending):
    priority = 240
    label_prefix = 32302
    params = {'info': 'random_likedlists'}
    art_icon = 'resources/icons/trakt/likedlist.png'
    types = ('both', )


class BaseDirItemRandomMyLists(BaseDirItemRandomTrending):
    priority = 250
    label_prefix = 32303
    params = {'info': 'random_mylists'}
    art_icon = 'resources/icons/trakt/mylists.png'
    types = ('both', )


def get_all_random_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
