"""
BASEMETA FACTORY

Addons for BASEITEM to retrieve additional details from related database tables (e.g. genres of a movie)
and/or to sync mapped data back to those tables

"""


def import_crewmember():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import CrewMember
    return CrewMember


def import_castmember():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import CastMember
    return CastMember


def import_creator():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Creator
    return Creator


def import_director():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Director
    return Director


def import_writer():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Writer
    return Writer


def import_screenplay():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Screenplay
    return Screenplay


def import_producer():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Producer
    return Producer


def import_sound_department():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import SoundDepartment
    return SoundDepartment


def import_art_department():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import ArtDepartment
    return ArtDepartment


def import_photography():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Photography
    return Photography


def import_editor():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Editor
    return Editor


def import_person():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.credits import Person
    return Person


def import_starredmovies():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.appearances import StarredMovies
    return StarredMovies


def import_starredtvshows():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.appearances import StarredTVShows
    return StarredTVShows


def import_crewedmovies():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.appearances import CrewedMovies
    return CrewedMovies


def import_crewedtvshows():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.appearances import CrewedTVShows
    return CrewedTVShows


def import_base():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Base
    return Base


def import_collection():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Series
    return Series


def import_belongs():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Belongs
    return Belongs


def import_movie():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Movie
    return Movie


def import_tvshow():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Tvshow
    return Tvshow


def import_season():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Season
    return Season


def import_episode():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Episode
    return Episode


def import_unique_id():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import UniqueId
    return UniqueId


def import_custom():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Custom
    return Custom


def import_genre():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Genre
    return Genre


def import_country():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Country
    return Country


def import_video():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Video
    return Video


def import_certification():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Certification
    return Certification


def import_translation():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Translation
    return Translation


def import_company():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Company
    return Company


def import_broadcaster():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Broadcaster
    return Broadcaster


def import_service():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Service
    return Service


def import_studio():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Studio
    return Studio


def import_network():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Network
    return Network


def import_provider():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.info import Provider
    return Provider


def import_fanart_tv():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTV
    return FanartTV


def import_fanart_tv_poster():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVPoster
    return FanartTVPoster


def import_fanart_tv_poster_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVPosterLanguage
    return FanartTVPosterLanguage


def import_fanart_tv_poster_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVPosterEnglish
    return FanartTVPosterEnglish


def import_fanart_tv_poster_null():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVPosterNull
    return FanartTVPosterNull


def import_fanart_tv_fanart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVFanart
    return FanartTVFanart


def import_fanart_tv_landscape():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVLandscape
    return FanartTVLandscape


def import_fanart_tv_landscape_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVLandscapeLanguage
    return FanartTVLandscapeLanguage


def import_fanart_tv_landscape_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVLandscapeEnglish
    return FanartTVLandscapeEnglish


def import_fanart_tv_clearlogo():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVClearlogo
    return FanartTVClearlogo


def import_fanart_tv_clearlogo_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVClearlogoLanguage
    return FanartTVClearlogoLanguage


def import_fanart_tv_clearlogo_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVClearlogoEnglish
    return FanartTVClearlogoEnglish


def import_fanart_tv_clearlogo_null():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVClearlogoNull
    return FanartTVClearlogoNull


def import_fanart_tv_clearart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVClearart
    return FanartTVClearart


def import_fanart_tv_banner():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVBanner
    return FanartTVBanner


def import_fanart_tv_discart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.fanart_tv import FanartTVDiscart
    return FanartTVDiscart


def import_art():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import Art
    return Art


def import_art_profile():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtProfile
    return ArtProfile


def import_art_poster():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtPoster
    return ArtPoster


def import_art_poster_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtPosterLanguage
    return ArtPosterLanguage


def import_art_poster_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtPosterEnglish
    return ArtPosterEnglish


def import_art_poster_null():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtPosterNull
    return ArtPosterNull


def import_art_fanart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtFanart
    return ArtFanart


def import_art_extrafanart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtExtraFanart
    return ArtExtraFanart


def import_art_landscape():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtLandscape
    return ArtLandscape


def import_art_landscape_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtLandscapeLanguage
    return ArtLandscapeLanguage


def import_art_landscape_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtLandscapeEnglish
    return ArtLandscapeEnglish


def import_art_thumbs():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtThumbs
    return ArtThumbs


def import_art_clearlogo():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtClearlogo
    return ArtClearlogo


def import_art_clearlogo_language():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtClearlogoLanguage
    return ArtClearlogoLanguage


def import_art_clearlogo_english():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtClearlogoEnglish
    return ArtClearlogoEnglish


def import_art_clearlogo_null():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.art import ArtClearlogoNull
    return ArtClearlogoNull


def import_user_art_poster():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.user_art import UserArtPoster
    return UserArtPoster


def import_user_art_fanart():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.user_art import UserArtFanart
    return UserArtFanart


def import_user_art_landscape():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.user_art import UserArtLandscape
    return UserArtLandscape


def import_user_art_clearlogo():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.user_art import UserArtClearlogo
    return UserArtClearlogo


def import_user_art_thumb():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.user_art import UserArtThumb
    return UserArtThumb


def import_playcount():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import PlayCount
    return PlayCount


def import_watchedcount():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import WatchedCount
    return WatchedCount


def import_airedcount():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import AiredCount
    return AiredCount


def import_playprogress():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import PlayProgress
    return PlayProgress


def import_favorites_rank():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import FavoritesRank
    return FavoritesRank


def import_watchlist_rank():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import WatchlistRank
    return WatchlistRank


def import_collected_date():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import CollectedDate
    return CollectedDate


def import_lastplayed():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.trakt import LastPlayed
    return LastPlayed


def import_series_genre():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.series import SeriesGenre
    return SeriesGenre


def import_series_movie():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.series import SeriesMovie
    return SeriesMovie


def import_series_stats():
    from tmdbhelper.lib.items.database.basemeta_factories.concrete_classes.series import SeriesStats
    return SeriesStats


FACTORY_ROUTES = {
    'crewmember': import_crewmember,
    'castmember': import_castmember,
    'creator': import_creator,
    'director': import_director,
    'writer': import_writer,
    'screenplay': import_screenplay,
    'producer': import_producer,
    'sound_department': import_sound_department,
    'art_department': import_art_department,
    'photography': import_photography,
    'editor': import_editor,
    'person': import_person,
    'starredmovies': import_starredmovies,
    'starredtvshows': import_starredtvshows,
    'crewedmovies': import_crewedmovies,
    'crewedtvshows': import_crewedtvshows,
    'base': import_base,
    'movie': import_movie,
    'tvshow': import_tvshow,
    'season': import_season,
    'episode': import_episode,
    'belongs': import_belongs,
    'collection': import_collection,
    'unique_id': import_unique_id,
    'custom': import_custom,
    'genre': import_genre,
    'country': import_country,
    'video': import_video,
    'certification': import_certification,
    'translation': import_translation,
    'company': import_company,
    'broadcaster': import_broadcaster,
    'service': import_service,
    'network': import_network,
    'studio': import_studio,
    'provider': import_provider,
    'fanart_tv': import_fanart_tv,
    'fanart_tv_poster': import_fanart_tv_poster,
    'fanart_tv_poster_language': import_fanart_tv_poster_language,
    'fanart_tv_poster_english': import_fanart_tv_poster_english,
    'fanart_tv_poster_null': import_fanart_tv_poster_null,
    'fanart_tv_fanart': import_fanart_tv_fanart,
    'fanart_tv_landscape': import_fanart_tv_landscape,
    'fanart_tv_landscape_language': import_fanart_tv_landscape_language,
    'fanart_tv_landscape_english': import_fanart_tv_landscape_english,
    'fanart_tv_clearlogo': import_fanart_tv_clearlogo,
    'fanart_tv_clearlogo_language': import_fanart_tv_clearlogo_language,
    'fanart_tv_clearlogo_english': import_fanart_tv_clearlogo_english,
    'fanart_tv_clearlogo_null': import_fanart_tv_clearlogo_null,
    'fanart_tv_clearart': import_fanart_tv_clearart,
    'fanart_tv_banner': import_fanart_tv_banner,
    'fanart_tv_discart': import_fanart_tv_discart,
    'art': import_art,
    'art_profile': import_art_profile,
    'art_poster': import_art_poster,
    'art_poster_language': import_art_poster_language,
    'art_poster_english': import_art_poster_english,
    'art_poster_null': import_art_poster_null,
    'art_fanart': import_art_fanart,
    'art_extrafanart': import_art_extrafanart,
    'art_landscape': import_art_landscape,
    'art_landscape_language': import_art_landscape_language,
    'art_landscape_english': import_art_landscape_english,
    'art_thumbs': import_art_thumbs,
    'art_clearlogo': import_art_clearlogo,
    'art_clearlogo_language': import_art_clearlogo_language,
    'art_clearlogo_english': import_art_clearlogo_english,
    'art_clearlogo_null': import_art_clearlogo_null,
    'user_art_poster': import_user_art_poster,
    'user_art_fanart': import_user_art_fanart,
    'user_art_landscape': import_user_art_landscape,
    'user_art_clearlogo': import_user_art_clearlogo,
    'user_art_thumb': import_user_art_thumb,
    'playcount': import_playcount,
    'watchedcount': import_watchedcount,
    'airedcount': import_airedcount,
    'playprogress': import_playprogress,
    'favorites_rank': import_favorites_rank,
    'watchlist_rank': import_watchlist_rank,
    'collected_date': import_collected_date,
    'lastplayed': import_lastplayed,
    'series_genre': import_series_genre,
    'series_movie': import_series_movie,
    'series_stats': import_series_stats,
}


def BaseMetaFactory(route):
    return FACTORY_ROUTES[route]()()
