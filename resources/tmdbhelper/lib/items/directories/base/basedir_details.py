from tmdbhelper.lib.addon.plugin import get_flatseasons_info_param
from tmdbhelper.lib.items.directories.base.basedir_item import BaseDirItem
from jurialmunkey.ftools import cached_property


class BaseDirItemDetailsPlay(BaseDirItem):
    priority = 100
    label_type = 'localize'
    label_localized = 208
    params = {'info': 'play'}
    art_icon = 'resources/icons/themoviedb/default.png'
    types = ('movie', 'episode', )


class BaseDirItemDetailsSeasons(BaseDirItem):
    priority = 110
    label_type = 'localize'
    label_localized = 33054
    art_icon = 'resources/icons/themoviedb/episodes.png'
    types = ('tv', 'episode', )

    @cached_property
    def params(self):
        return {'info': get_flatseasons_info_param()}


class BaseDirItemDetailsCollection(BaseDirItem):
    priority = 120
    label_type = 'localize'
    label_localized = 32192
    params = {'info': 'collection'}
    art_icon = 'resources/icons/themoviedb/movies.png'
    types = ('movie', )


class BaseDirItemDetailsEpisodes(BaseDirItem):
    priority = 130
    label_type = 'localize'
    label_localized = 20360
    params = {'info': 'episodes'}
    art_icon = 'resources/icons/themoviedb/episodes.png'
    types = ('episode',)


class BaseDirItemDetailsCast(BaseDirItem):
    priority = 140
    label_type = 'localize'
    label_localized = 206
    params = {'info': 'cast', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/cast.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsRecommendations(BaseDirItem):
    priority = 150
    label_type = 'localize'
    label_localized = 32223
    params = {'info': 'recommendations', 'cacheonly': 'true'}
    art_icon = 'resources/icons/themoviedb/recommended.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsTraktRelated(BaseDirItem):
    priority = 160
    label_type = 'localize'
    label_localized = 32064
    params = {'info': 'trakt_related'}
    art_icon = 'resources/icons/trakt/popular.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsSimilar(BaseDirItem):
    priority = 170
    label_type = 'localize'
    label_localized = 32224
    params = {'info': 'similar', 'cacheonly': 'true'}
    art_icon = 'resources/icons/themoviedb/similar.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsCrew(BaseDirItem):
    priority = 180
    label_type = 'localize'
    label_localized = 32225
    params = {'info': 'crew', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/cast.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsPosters(BaseDirItem):
    priority = 190
    label_type = 'localize'
    label_localized = 32226
    params = {'info': 'posters'}
    art_icon = 'resources/icons/themoviedb/images.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsFanart(BaseDirItem):
    priority = 200
    label_type = 'localize'
    label_localized = 20445
    params = {'info': 'fanart'}
    art_icon = 'resources/icons/themoviedb/images.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsMovieKeywords(BaseDirItem):
    priority = 210
    label_type = 'localize'
    label_localized = 21861
    params = {'info': 'movie_keywords'}
    art_icon = 'resources/icons/themoviedb/tags.png'
    types = ('movie',)


class BaseDirItemDetailsReviews(BaseDirItem):
    priority = 220
    label_type = 'localize'
    label_localized = 32188
    params = {'info': 'reviews'}
    art_icon = 'resources/icons/themoviedb/reviews.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsTraktComments(BaseDirItem):
    priority = 230
    label_type = 'localize'
    label_localized = 32305
    params = {'info': 'trakt_comments'}
    art_icon = 'resources/icons/trakt/mylists.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsTraktWatchers(BaseDirItem):
    priority = 240
    label_type = 'localize'
    label_localized = 32065
    params = {'info': 'trakt_watchers'}
    art_icon = 'resources/icons/trakt/popularlist.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsStarsInMovies(BaseDirItem):
    priority = 250
    label_type = 'localize'
    label_localized = 32227
    params = {'info': 'stars_in_movies', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/movies.png'
    types = ('person',)


class BaseDirItemDetailsStarsInTVShows(BaseDirItem):
    priority = 260
    label_type = 'localize'
    label_localized = 32228
    params = {'info': 'stars_in_tvshows', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/tv.png'
    types = ('person',)


class BaseDirItemDetailsCrewInMovies(BaseDirItem):
    priority = 270
    label_type = 'localize'
    label_localized = 32229
    params = {'info': 'crew_in_movies', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/movies.png'
    types = ('person',)


class BaseDirItemDetailsCrewInTVShows(BaseDirItem):
    priority = 280
    label_type = 'localize'
    label_localized = 32230
    params = {'info': 'crew_in_tvshows', 'cacheonly': 'true', 'limit': 250}
    art_icon = 'resources/icons/themoviedb/tv.png'
    types = ('person',)


class BaseDirItemDetailsImages(BaseDirItem):
    priority = 290
    label_type = 'localize'
    label_localized = 32191
    params = {'info': 'images'}
    art_icon = 'resources/icons/themoviedb/images.png'
    types = ('person',)


class BaseDirItemDetailsEpisodeThumbs(BaseDirItem):
    priority = 300
    label_type = 'localize'
    label_localized = 32231
    params = {'info': 'episode_thumbs'}
    art_icon = 'resources/icons/themoviedb/images.png'
    types = ('episode',)


class BaseDirItemDetailsVideos(BaseDirItem):
    priority = 310
    label_type = 'localize'
    label_localized = 10025
    params = {'info': 'videos'}
    art_icon = 'resources/icons/themoviedb/movies.png'
    types = ('movie', 'tv', 'episode',)


class BaseDirItemDetailsTraktInLists(BaseDirItem):
    priority = 320
    label_type = 'localize'
    label_localized = 32232
    params = {'info': 'trakt_inlists'}
    art_icon = 'resources/icons/themoviedb/trakt.png'
    types = ('movie', 'tv', 'episode',)


def get_all_details_class_instances(include_play=True, **kwargs):

    def condition_func(member):
        if not include_play and member.__name__ == 'BaseDirItemDetailsPlay':
            return False
        return True

    from tmdbhelper.lib.items.directories.base.item_details_builder import configure
    from tmdbhelper.lib.addon.module import get_all_module_class_objects_by_priority
    return [configure(i, **kwargs) for i in get_all_module_class_objects_by_priority(__name__, condition_func)]
