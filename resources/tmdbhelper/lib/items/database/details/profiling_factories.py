"""Configured factory subclasses used only by detailed service reports."""

from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.movie import Movie
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.tvshow import Tvshow
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.season import Season
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode import Episode
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.person import Person
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.series import Series
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode_group import EpisodeGroup
from tmdbhelper.lib.items.database.baseitem_factories.concrete_classes.episode_group_season import EpisodeGroupSeason
from tmdbhelper.lib.items.database.details.backend import DetailsLookup
from tmdbhelper.lib.items.database.details.profiling_items import ProfiledItemMetaFactory


class ProfiledFactoryMixin:
    item_meta_factory = staticmethod(ProfiledItemMetaFactory)

    def get_item_meta(self, data):
        return self.cache.profiler.call_stage('item_mapping', super().get_item_meta, data)


class ProfiledMovie(ProfiledFactoryMixin, Movie):
    pass


class ProfiledTvshow(ProfiledFactoryMixin, Tvshow):
    pass


class ProfiledSeason(ProfiledFactoryMixin, Season):
    pass


class ProfiledEpisode(ProfiledFactoryMixin, Episode):
    pass


class ProfiledPerson(ProfiledFactoryMixin, Person):
    pass


class ProfiledSeries(ProfiledFactoryMixin, Series):
    pass


class ProfiledEpisodeGroup(ProfiledFactoryMixin, EpisodeGroup):
    pass


class ProfiledEpisodeGroupSeason(ProfiledFactoryMixin, EpisodeGroupSeason):
    pass


FACTORY_ROUTES = {
    'movie': ProfiledMovie,
    'tvshow': ProfiledTvshow,
    'season': ProfiledSeason,
    'episode': ProfiledEpisode,
    'person': ProfiledPerson,
    'set': ProfiledSeries,
    'episode_group': ProfiledEpisodeGroup,
    'episode_group_season': ProfiledEpisodeGroupSeason,
}


def ProfiledBaseItemFactory(mediatype, *args, **kwargs):
    try:
        factory = FACTORY_ROUTES[mediatype](*args, **kwargs)
    except KeyError:
        return
    factory.mediatype = mediatype
    return factory


class ProfiledDetailsLookup(DetailsLookup):
    item_factory = staticmethod(ProfiledBaseItemFactory)
