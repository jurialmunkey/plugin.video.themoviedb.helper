from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from tmdbhelper.lib.addon.plugin import get_localized
from jurialmunkey.ftools import cached_property


class BaseDirItemTMDbSearch(BaseDirItem):
    priority = 100
    label_localized = 137
    params = {'info': 'dir_search'}
    art_icon = 'resources/icons/themoviedb/search.png'
    types = ('movie', 'tv', 'person')


class BaseDirItemTMDbPopular(BaseDirItem):
    priority = 110
    label_localized = 32175
    params = {'info': 'popular'}
    art_icon = 'resources/icons/themoviedb/popular.png'
    types = ('movie', 'tv', 'person')


class BaseDirItemTMDbTopRated(BaseDirItem):
    priority = 120
    label_localized = 32176
    params = {'info': 'top_rated'}
    art_icon = 'resources/icons/themoviedb/toprated.png'
    types = ('movie', 'tv')


class BaseDirItemTMDbUpcoming(BaseDirItem):
    priority = 130
    label_localized = 32177
    params = {'info': 'upcoming'}
    art_icon = 'resources/icons/themoviedb/upcoming.png'
    types = ('movie', )
    
class BaseDirItemTMDbTrendingDay(BaseDirItem):
    priority = 140
    label_localized = 32178
    params = {'info': 'trending_day'}
    art_icon = 'resources/icons/themoviedb/upcoming.png'
    types = ('movie', 'tv', 'person')


class BaseDirItemTMDbTrendingWeek(BaseDirItem):
    priority = 150
    label_localized = 32179
    params = {'info': 'trending_week'}
    art_icon = 'resources/icons/themoviedb/upcoming.png'
    types = ('movie', 'tv', 'person')


class BaseDirItemTMDbNowPlaying(BaseDirItem):
    priority = 160
    label_localized = 32180
    params = {'info': 'now_playing'}
    art_icon = 'resources/icons/themoviedb/intheatres.png'
    types = ('movie', )


class BaseDirItemTMDbAiringToday(BaseDirItem):
    priority = 170
    label_type = 'localize'
    label_localized = 32181
    types = ('tv',)
    params = {'info': 'airing_today'}
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemTMDbOnTheAir(BaseDirItem):
    priority = 180
    label_type = 'localize'
    label_localized = 32182
    types = ('tv',)
    params = {'info': 'on_the_air'}
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemTMDbCalendarLibraryDir(BaseDirItem):
    priority = 190
    label_type = 'localize'
    label_localized = 32183
    types = ('tv',)
    params = {'info': 'dir_calendar_library'}
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemTMDbLibraryAiringNext(BaseDirItem):
    priority = 200
    label_type = 'localize'
    label_localized = 32458
    types = ('tv',)
    params = {'info': 'library_airingnext'}
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemTMDbGenres(BaseDirItem):
    priority = 210
    label_type = 'reversed'
    label_localized = 135
    types = ('movie', 'tv',)
    params = {'info': 'genres'}
    art_icon = 'resources/icons/themoviedb/genre.png'


class BaseDirItemTMDbWatchProviders(BaseDirItem):
    priority = 220
    label_type = 'reversed'
    label_localized = 32411
    types = ('movie', 'tv',)
    params = {'info': 'watch_providers'}
    art_icon = 'resources/icons/themoviedb/airing.png'


class BaseDirItemTMDbRevenueMovies(BaseDirItem):
    priority = 230
    label_localized = 32184
    types = ('movie',)
    params = {'info': 'revenue_movies'}
    art_icon = 'resources/icons/themoviedb/default.png'


class BaseDirItemTMDbMostVoted(BaseDirItem):
    priority = 240
    label_localized = 32185
    types = ('movie', 'tv',)
    params = {'info': 'most_voted'}
    art_icon = 'resources/icons/themoviedb/default.png'


class BaseDirItemTMDbAllStudios(BaseDirItem):
    priority = 250
    label_type = 'prefixed'
    label_localized = 20388
    types = ('movie',)
    params = {'info': 'all_studios'}
    art_icon = 'resources/icons/themoviedb/default.png'

    @cached_property
    def label_prefixed(self):
        return get_localized(593)


class BaseDirItemTMDbAllNetworks(BaseDirItemTMDbAllStudios):
    priority = 260
    label_localized = 32062
    types = ('tv',)
    params = {'info': 'all_networks'}


class BaseDirItemTMDbAllCollections(BaseDirItemTMDbAllStudios):
    priority = 270
    label_localized = 32187
    types = ('movie',)
    params = {'info': 'all_collections'}


class BaseDirItemTMDbAllKeywords(BaseDirItemTMDbAllStudios):
    priority = 280
    label_localized = 21861
    types = ('movie',)
    params = {'info': 'all_keywords'}


def get_all_tmdb_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
