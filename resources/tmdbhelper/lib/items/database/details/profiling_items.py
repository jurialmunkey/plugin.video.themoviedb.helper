"""Opt-in mapping timers using the same output pipeline as regular item mappers."""

from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.movie import Movie
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.tvshow import Tvshow
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.season import Season
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.episode import Episode
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.person import Person
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.series import Series
from tmdbhelper.lib.items.database.itemmeta_factories.concrete_classes.episode_group import (
    EpisodeGroup, EpisodeGroupSeason,
)


class ProfiledItemMixin:
    def profile(self, stage, func, *args):
        return self.parent_db_cache.cache.profiler.call_stage(stage, func, *args)

    def get_stable_item(self):
        return self.profile('metadata_assembly', super().get_stable_item)

    def get_stable_infolabels(self):
        return self.profile('label_mapping', super().get_stable_infolabels)

    def get_infoproperties_dbclist(self, infoproperties):
        return self.profile(
            'extended_mapping', super().get_infoproperties_dbclist, infoproperties)

    def get_infoproperties_special(self, infoproperties):
        return self.profile(
            'related_properties_mapping', super().get_infoproperties_special, infoproperties)

    def get_infoproperties_dbcitem(self, infoproperties):
        return self.profile(
            'fresh_properties_mapping', super().get_infoproperties_dbcitem, infoproperties)

    def get_infoproperties_fresh(self, infoproperties):
        return self.profile(
            'fresh_state_mapping', super().get_infoproperties_fresh, infoproperties)

    def get_infoproperties_airdate(self, infoproperties):
        return self.profile(
            'airdate_mapping', super().get_infoproperties_airdate, infoproperties)

    def get_art_dbclist(self, art):
        return self.profile('artwork_mapping', super().get_art_dbclist, art)

    def get_profiled_infolabels(self):
        return super().infolabels

    @cached_property
    def infolabels(self):
        return self.profile('fresh_labels_mapping', self.get_profiled_infolabels)

    def get_profiled_cast(self):
        return super().cast

    @cached_property
    def cast(self):
        return self.profile('cast_mapping', self.get_profiled_cast)

    def get_profiled_unique_ids(self):
        return super().unique_ids

    @cached_property
    def unique_ids(self):
        return self.profile('unique_ids_mapping', self.get_profiled_unique_ids)


class ProfiledMovie(ProfiledItemMixin, Movie):
    pass


class ProfiledTvshow(ProfiledItemMixin, Tvshow):
    pass


class ProfiledSeason(ProfiledItemMixin, Season):
    pass


class ProfiledEpisode(ProfiledItemMixin, Episode):
    pass


class ProfiledPerson(ProfiledItemMixin, Person):
    pass


class ProfiledSeries(ProfiledItemMixin, Series):
    pass


class ProfiledEpisodeGroup(ProfiledItemMixin, EpisodeGroup):
    pass


class ProfiledEpisodeGroupSeason(ProfiledItemMixin, EpisodeGroupSeason):
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


def ProfiledItemMetaFactory(parent_db_cache, data):
    mapper = FACTORY_ROUTES[parent_db_cache.mediatype](parent_db_cache)
    mapper.mediatype = parent_db_cache.mediatype
    mapper.data = data
    return mapper
