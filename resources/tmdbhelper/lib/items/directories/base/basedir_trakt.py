from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized


class BaseDirItemTraktCollection(BaseDirItem):
    priority = 100
    label_localized = 32192
    label_type = 'reversed'
    params = {'info': 'trakt_collection'}
    art_icon = '/resources/icons/trakt/watchlist.png'
    types = ('movie', 'tv', 'both')


class BaseDirItemTraktFavorites(BaseDirItem):
    priority = 110
    label_type = 'reversed'
    label_localized = 1036
    types = ('movie', 'tv', 'both', )
    params = {'info': 'trakt_favorites'}
    sorting = True
    art_icon = 'resources/icons/trakt/watchlist.png'


class BaseDirItemTraktWatchlist(BaseDirItem):
    priority = 120
    label_type = 'reversed'
    label_localized = 32193
    types = ('movie', 'tv', 'season', 'episode', 'both', )
    params = {'info': 'trakt_watchlist'}
    sorting = True
    art_icon = 'resources/icons/trakt/watchlist.png'


class BaseDirItemTraktWatchListReleased(BaseDirItemTraktWatchlist):
    priority = 130
    label_type = 'reversed'
    label_localized = 32456
    params = {'info': 'trakt_watchlist_released'}


class BaseDirItemTraktWatchListAnticipated(BaseDirItemTraktWatchlist):
    priority = 140
    label_type = 'reversed'
    label_localized = 32457
    params = {'info': 'trakt_watchlist_anticipated'}


class BaseDirItemTraktHistory(BaseDirItem):
    priority = 150
    label_localized = 32194
    types = ('movie', 'tv', 'episode', 'both', )
    params = {'info': 'trakt_history'}
    art_icon = 'resources/icons/trakt/recentlywatched.png'


class BaseDirItemTraktMostWatched(BaseDirItem):
    priority = 160
    label_localized = 32195
    types = ('movie', 'tv', 'episode', )
    params = {'info': 'trakt_mostwatched'}
    art_icon = 'resources/icons/trakt/mostwatched.png'


class BaseDirItemTraktInProgress(BaseDirItem):
    priority = 170
    label_localized = 32196
    types = ('movie', 'tv', )
    params = {'info': 'trakt_inprogress'}
    sorting = True
    art_icon = 'resources/icons/trakt/inprogress.png'


class BaseDirItemTraktOnDeck(BaseDirItem):
    priority = 180
    label_type = 'localize'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'trakt_ondeck'}
    art_icon = 'resources/icons/trakt/inprogress.png'


class BaseDirItemTraktOnDeckUnWatchedMovie(BaseDirItem):
    priority = 190
    label_type = 'appended'
    label_localized = 32196
    types = ('movie', )
    params = {'info': 'trakt_ondeck_unwatched'}
    art_icon = 'resources/icons/trakt/inprogress.png'

    @cached_property
    def label_append(self):
        return get_localized(16101)


class BaseDirItemTraktOnDeckUnWatchedTV(BaseDirItem):
    priority = 200
    label_type = 'suffixed'
    label_localized = 32406
    types = ('tv', )
    params = {'info': 'trakt_ondeck_unwatched'}
    art_icon = 'resources/icons/trakt/inprogress.png'

    @cached_property
    def label_suffix(self):
        return f'({get_localized(16101)})'


class BaseDirItemTraktToWatch(BaseDirItem):
    priority = 210
    label_type = 'reversed'
    label_localized = 32078
    types = ('movie', 'tv', )
    params = {'info': 'trakt_towatch'}
    art_icon = 'resources/icons/trakt/watchlist.png'


class BaseDirItemTraktNextEpisodes(BaseDirItem):
    priority = 220
    label_type = 'localize'
    label_localized = 32197
    types = ('tv', )
    params = {'info': 'trakt_nextepisodes'}
    art_icon = 'resources/icons/trakt/inprogress.png'


class BaseDirItemTraktDropped(BaseDirItem):
    priority = 230
    label_type = 'localize'
    label_localized = 32048
    types = ('tv', )
    params = {'info': 'trakt_dropped'}
    art_icon = 'resources/icons/trakt/inprogress.png'


class BaseDirItemTraktRecommendations(BaseDirItem):
    priority = 240
    label_type = 'reversed'
    label_localized = 32198
    types = ('movie', 'tv', )
    params = {'info': 'trakt_recommendations'}
    art_icon = 'resources/icons/trakt/recommended.png'


class BaseDirItemTraktBecauseYouWatched(BaseDirItem):
    priority = 250
    label_localized = 32199
    types = ('movie', 'tv', )
    params = {'info': 'trakt_becauseyouwatched'}
    art_icon = 'resources/icons/trakt/recommended.png'


class BaseDirItemTraktBecauseMostWatched(BaseDirItem):
    priority = 260
    label_localized = 32200
    types = ('movie', 'tv', )
    params = {'info': 'trakt_becausemostwatched'}
    art_icon = 'resources/icons/trakt/recommended.png'


class BaseDirItemTraktMyAiring(BaseDirItem):
    priority = 270
    types = ('tv', )
    params = {'info': 'trakt_myairing'}
    art_icon = 'resources/icons/trakt/airing.png'

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_prefix(self):
        return get_localized(32201)

    @cached_property
    def label_append(self):
        return get_localized(32202)


class BaseDirItemTraktAiringNext(BaseDirItem):
    priority = 280
    label_type = 'localize'
    label_localized = 32459
    types = ('tv', )
    params = {'info': 'trakt_airingnext'}
    art_icon = 'resources/icons/trakt/calendar.png'


class BaseDirItemTraktCalendarDir(BaseDirItem):
    priority = 290
    types = ('tv', )
    params = {'info': 'dir_calendar_trakt'}
    art_icon = 'resources/icons/trakt/calendar.png'

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_prefix(self):
        return get_localized(32201)

    @cached_property
    def label_append(self):
        return get_localized(32203)


class BaseDirItemTraktMovieCalendarDir(BaseDirItemTraktCalendarDir):
    priority = 291
    types = ('movie', )
    params = {'info': 'dir_calendar_movie'}

    @cached_property
    def label_append(self):
        return f'{get_localized(32416)} {get_localized(32203)}'


class BaseDirItemTraktDVDCalendarDir(BaseDirItemTraktCalendarDir):
    priority = 292
    types = ('movie', )
    params = {'info': 'dir_calendar_dvd'}

    @cached_property
    def label_prefix(self):
        return f'{get_localized(32201)} DVD'


class BaseDirItemTraktCalendarPremieresDir(BaseDirItemTraktCalendarDir):
    priority = 300
    params = {'info': 'dir_calendar_trakt', 'endpoint': 'premieres'}

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append} {label_suffix}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_suffix(self):
        return get_localized(32416)


class BaseDirItemTraktCalendarNewDir(BaseDirItemTraktCalendarPremieresDir):
    priority = 310
    params = {'info': 'dir_calendar_trakt', 'endpoint': 'new'}

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append} {label_suffix}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_suffix(self):
        return get_localized(842)


class BaseDirItemTraktCalendarAllDir(BaseDirItemTraktCalendarPremieresDir):
    priority = 320
    params = {'info': 'dir_calendar_trakt', 'user': 'false'}

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_prefix(self):
        return get_localized(32186)


class BaseDirItemTraktCalendarPremieresAllDir(BaseDirItemTraktCalendarPremieresDir):
    priority = 330
    params = {'info': 'dir_calendar_trakt', 'user': 'false', 'endpoint': 'premieres'}

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append} {label_suffix}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_prefix(self):
        return get_localized(32186)

    @cached_property
    def label_suffix(self):
        return get_localized(32416)


class BaseDirItemTraktMovieCalendarAllDir(BaseDirItemTraktCalendarDir):
    priority = 331
    types = ('movie', )
    params = {'info': 'dir_calendar_movie', 'user': 'false'}

    @cached_property
    def label_prefix(self):
        return get_localized(32186)

    @cached_property
    def label_append(self):
        return f'{get_localized(32416)} {get_localized(32203)}'


class BaseDirItemTraktDVDCalendarAllDir(BaseDirItemTraktCalendarDir):
    priority = 332
    types = ('movie', )
    params = {'info': 'dir_calendar_dvd', 'user': 'false'}

    @cached_property
    def label_prefix(self):
        return f'{get_localized(32186)} DVD'


class BaseDirItemTraktCalendarNewAllDir(BaseDirItemTraktCalendarPremieresAllDir):
    priority = 340
    params = {'info': 'dir_calendar_trakt', 'user': 'false', 'endpoint': 'new'}

    @cached_property
    def label(self):
        return '{label_prefix} {{item_type}}{{space}}{label_append} {label_suffix}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_suffix(self):
        return get_localized(842)


class BaseDirItemTraktGenres(BaseDirItem):
    priority = 350
    label_type = 'reversed'
    label_localized = 135
    types = ('movie', 'tv', )
    params = {'info': 'trakt_genres'}
    art_icon = 'resources/icons/trakt/genres.png'


class BaseDirItemTraktYears(BaseDirItem):
    priority = 360
    label_type = 'reversed'
    label_localized = 652
    types = ('movie', 'tv', )
    params = {'info': 'trakt_years'}
    art_icon = 'resources/icons/trakt/calendar.png'


class BaseDirItemTraktTrending(BaseDirItem):
    priority = 370
    label_localized = 32204
    types = ('movie', 'tv', )
    params = {'info': 'trakt_trending'}
    filters = True
    art_icon = 'resources/icons/trakt/trend.png'


class BaseDirItemTraktPopular(BaseDirItem):
    priority = 380
    label_localized = 32175
    types = ('movie', 'tv', )
    params = {'info': 'trakt_popular'}
    filters = True
    art_icon = 'resources/icons/trakt/popular.png'


class BaseDirItemTraktMostPlayed(BaseDirItem):
    priority = 390
    label_localized = 32205
    types = ('movie', 'tv', )
    params = {'info': 'trakt_mostplayed'}
    filters = True
    art_icon = 'resources/icons/trakt/mostplayed.png'


class BaseDirItemTraktMostViewers(BaseDirItem):
    priority = 400
    label_localized = 32414
    types = ('movie', 'tv', )
    params = {'info': 'trakt_mostviewers'}
    filters = True
    art_icon = 'resources/icons/trakt/mostplayed.png'


class BaseDirItemTraktAntipated(BaseDirItem):
    priority = 410
    label_localized = 32206
    types = ('movie', 'tv', )
    params = {'info': 'trakt_anticipated'}
    filters = True
    art_icon = 'resources/icons/trakt/anticipated.png'


class BaseDirItemTraktBoxOffice(BaseDirItem):
    priority = 420
    label_localized = 32207
    types = ('movie', )
    params = {'info': 'trakt_boxoffice'}
    art_icon = 'resources/icons/trakt/boxoffice.png'


class BaseDirItemTraktPopularDecade2020s(BaseDirItem):
    priority = 430
    types = ('movie', 'tv', )
    filters = True
    art_icon = 'resources/icons/trakt/calendar.png'
    trakt_decade = 2020

    @cached_property
    def label(self):
        return '{label_prefix}{{space}}{{item_type}} {label_suffix}s'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_prefix(self):
        return get_localized(32175)

    @cached_property
    def label_suffix(self):
        return self.trakt_decade

    @cached_property
    def params(self):
        return {
            'info': 'trakt_popular',
            'years': f'{self.trakt_decade}-{self.trakt_decade + 9}'
        }


class BaseDirItemTraktPopularDecade2010s(BaseDirItemTraktPopularDecade2020s):
    priority = 440
    trakt_decade = 2010


class BaseDirItemTraktPopularDecade2000s(BaseDirItemTraktPopularDecade2020s):
    priority = 450
    trakt_decade = 2000


class BaseDirItemTraktPopularDecade1990s(BaseDirItemTraktPopularDecade2020s):
    priority = 460
    trakt_decade = 1990


class BaseDirItemTraktPopularDecade1980s(BaseDirItemTraktPopularDecade2020s):
    priority = 470
    trakt_decade = 1980


class BaseDirItemTraktPopularDecade1970s(BaseDirItemTraktPopularDecade2020s):
    priority = 480
    trakt_decade = 1970


class BaseDirItemTraktPopularDecade1960s(BaseDirItemTraktPopularDecade2020s):
    priority = 490
    trakt_decade = 1960


class BaseDirItemTraktPopularDecade1950s(BaseDirItemTraktPopularDecade2020s):
    priority = 500
    trakt_decade = 1950


class BaseDirItemTraktPopularDecade1940s(BaseDirItemTraktPopularDecade2020s):
    priority = 510
    trakt_decade = 1940


class BaseDirItemTraktPopularDecade1930s(BaseDirItemTraktPopularDecade2020s):
    priority = 520
    trakt_decade = 1930


class BaseDirItemTraktPopularDecade1920s(BaseDirItemTraktPopularDecade2020s):
    priority = 530
    trakt_decade = 1920


class BaseDirItemTraktPopularDecade1910s(BaseDirItemTraktPopularDecade2020s):
    priority = 540
    trakt_decade = 1910


class BaseDirItemTraktPopularDecade1900s(BaseDirItemTraktPopularDecade2020s):
    priority = 550
    trakt_decade = 1900


class BaseDirItemTraktPopularCertificationG(BaseDirItem):
    priority = 560
    types = ('movie', )
    filters = True
    art_icon = 'resources/icons/trakt/popular.png'
    trakt_certifications = 'g'

    @cached_property
    def label(self):
        return '{label_append} {label_suffix} {label_prefix}{{space}}{{item_type}}'.format(
            label_prefix=self.label_prefix,
            label_append=self.label_append,
            label_suffix=self.label_suffix,
        )

    @cached_property
    def label_append(self):
        return get_localized(32175)

    @cached_property
    def label_suffix(self):
        return self.trakt_certifications.upper()

    @cached_property
    def label_prefix(self):
        return get_localized(32486)

    @cached_property
    def params(self):
        return {
            'info': 'trakt_popular',
            'certifications': self.trakt_certifications,
        }


class BaseDirItemTraktPopularCertificationPG(BaseDirItemTraktPopularCertificationG):
    priority = 570
    trakt_certifications = 'pg'


class BaseDirItemTraktPopularCertificationPG13(BaseDirItemTraktPopularCertificationG):
    priority = 580
    trakt_certifications = 'pg-13'


class BaseDirItemTraktPopularCertificationR(BaseDirItemTraktPopularCertificationG):
    priority = 590
    trakt_certifications = 'r'


class BaseDirItemTraktPopularCertificationNR(BaseDirItemTraktPopularCertificationG):
    priority = 600
    trakt_certifications = 'nr'


class BaseDirItemTraktTrendingLists(BaseDirItem):
    priority = 610
    label_type = 'localize'
    label_localized = 32208
    types = ('both', )
    params = {'info': 'trakt_trendinglists'}
    art_icon = 'resources/icons/trakt/trendinglist.png'


class BaseDirItemTraktPopularLists(BaseDirItem):
    priority = 620
    label_type = 'localize'
    label_localized = 32209
    types = ('both', )
    params = {'info': 'trakt_popularlists'}
    art_icon = 'resources/icons/trakt/popularlist.png'


class BaseDirItemTraktLikedLists(BaseDirItem):
    priority = 630
    label_type = 'localize'
    label_localized = 32210
    types = ('both', )
    params = {'info': 'trakt_likedlists'}
    art_icon = 'resources/icons/trakt/likedlist.png'


class BaseDirItemTraktMyLists(BaseDirItem):
    priority = 640
    label_type = 'localize'
    label_localized = 32211
    types = ('both', )
    params = {'info': 'trakt_mylists'}
    art_icon = 'resources/icons/trakt/mylists.png'


class BaseDirItemTraktSearchLists(BaseDirItem):
    priority = 650
    label_type = 'localize'
    label_localized = 32361
    types = ('both', )
    params = {'info': 'trakt_searchlists'}
    art_icon = 'resources/icons/trakt/mylist.png'


def get_all_trakt_class_instances():
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [clobj() for clobj in get_all_module_class_objects_by_priority(__name__)]
