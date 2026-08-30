#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.itemdata import SyncItemData, SyncItem, SyncItemConstructor


class TraktSyncItemData(SyncItemData):

    def __init__(self, item, item_type):
        self.item = item
        self.item_type = item_type

    """
    season_number
    """
    @cached_property
    def season_number(self):
        return self.get_season_number()

    def get_season_number(self):
        if self.item_type == 'season':
            return self.item["season"]["number"]
        if self.item_type == 'episode':
            return self.item["episode"]["season"]

    """
    episode_number
    """
    @cached_property
    def episode_number(self):
        return self.get_episode_number()

    def get_episode_number(self):
        if self.item_type == 'episode':
            return self.item["episode"]["number"]

    """
    tmdb_id
    """
    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_tmdb_id(self):
        try:
            return self.item[self.parent_item_type]['ids']['tmdb']
        except (AttributeError, KeyError, TypeError):
            return

    """
    trakt_slug
    """
    @cached_property
    def trakt_slug(self):
        return self.get_trakt_slug()

    def get_trakt_slug(self):
        try:
            return self.item[self.parent_item_type]['ids']['slug']
        except (AttributeError, KeyError, TypeError):
            return

    """
    plays
    """
    @cached_property
    def plays(self):
        return self.get_plays()

    def get_plays(self):
        return self.item.get('plays')

    """
    last_watched_at
    """
    @cached_property
    def last_watched_at(self):
        return self.get_last_watched_at()

    def get_last_watched_at(self):
        return self.item.get('last_watched_at') or self.item.get('watched_at')

    """
    aired_episodes
    """
    @cached_property
    def aired_episodes(self):
        return self.get_aired_episodes()

    def get_aired_episodes(self):
        try:
            return self.item['show']['aired_episodes']
        except (AttributeError, KeyError, TypeError):
            return
    """
    reset_at
    """
    @cached_property
    def reset_at(self):
        return self.get_reset_at()

    def get_reset_at(self):
        return self.item.get('reset_at')

    """
    rating
    """
    @cached_property
    def rating(self):
        return self.get_rating()

    def get_rating(self):
        return self.item.get('rating')

    """
    rated_at
    """
    @cached_property
    def rated_at(self):
        return self.get_rated_at()

    def get_rated_at(self):
        return self.item.get('rated_at')

    """
    rank
    """
    @cached_property
    def rank(self):
        return self.get_rank()

    def get_rank(self):
        return self.item.get('rank')

    """
    listed_at
    """
    @cached_property
    def listed_at(self):
        return self.get_listed_at()

    def get_listed_at(self):
        return self.item.get('listed_at')

    """
    notes
    """
    @cached_property
    def notes(self):
        return self.get_notes()

    def get_notes(self):
        return self.item.get('notes')

    """
    watched_episodes
    """
    @cached_property
    def watched_episodes(self):
        return self.get_watched_episodes()

    def get_watched_episodes(self):
        return

    """
    hidden_at
    """
    @cached_property
    def hidden_at(self):
        return self.get_hidden_at()

    def get_hidden_at(self):
        return self.item.get('hidden_at')

    """
    next_episode_id
    """
    @cached_property
    def next_episode_id(self):
        return self.get_next_episode_id()

    def get_next_episode_id(self):
        return self.item.get('next_episode_id')

    """
    next_episode_aired_at
    """
    @cached_property
    def next_episode_aired_at(self):
        return self.get_next_episode_aired_at()

    def get_next_episode_aired_at(self):
        return self.item.get('next_episode_aired_at')

    """
    upnext_episode_id
    """
    @cached_property
    def upnext_episode_id(self):
        return self.get_upnext_episode_id()

    def get_upnext_episode_id(self):
        return self.item.get('upnext_episode_id')

    """
    premiered
    """
    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        try:
            return self.item[self.parent_item_type]['first_aired'][:10]
        except (AttributeError, KeyError, TypeError):
            return

    """
    year
    """
    @cached_property
    def year(self):
        return self.get_year()

    def get_year(self):
        try:
            return self.item[self.parent_item_type]['year']
        except (AttributeError, KeyError, TypeError):
            return

    """
    title
    """
    @cached_property
    def title(self):
        return self.get_title()

    def get_title(self):
        try:
            return self.item[self.parent_item_type]['title']
        except (AttributeError, KeyError, TypeError):
            return

    """
    status
    """
    @cached_property
    def status(self):
        return self.get_status()

    def get_status(self):
        try:
            return self.item[self.parent_item_type]['status']
        except (AttributeError, KeyError, TypeError):
            return

    """
    country
    """
    @cached_property
    def country(self):
        return self.get_country()

    def get_country(self):
        try:
            return self.item[self.parent_item_type]['country']
        except (AttributeError, KeyError, TypeError):
            return

    """
    language
    """
    @cached_property
    def language(self):
        return self.get_language()

    def get_language(self):
        try:
            return self.item[self.parent_item_type]['language']
        except (AttributeError, KeyError, TypeError):
            return

    """
    certification
    """
    @cached_property
    def certification(self):
        return self.get_certification()

    def get_certification(self):
        try:
            return self.item[self.parent_item_type]['certification']
        except (AttributeError, KeyError, TypeError):
            return

    """
    runtime
    """
    @cached_property
    def runtime(self):
        return self.get_runtime()

    def get_runtime(self):
        try:
            return self.item[self.parent_item_type]['runtime']
        except (AttributeError, KeyError, TypeError):
            return

    """
    trakt_rating
    """
    @cached_property
    def trakt_rating(self):
        return self.get_trakt_rating()

    def get_trakt_rating(self):
        try:
            return self.item[self.parent_item_type]['rating']
        except (AttributeError, KeyError, TypeError):
            return

    """
    trakt_votes
    """
    @cached_property
    def trakt_votes(self):
        return self.get_trakt_votes()

    def get_trakt_votes(self):
        try:
            return self.item[self.parent_item_type]['votes']
        except (AttributeError, KeyError, TypeError):
            return


class TraktSyncItemConstructor(SyncItemConstructor):
    item_data_class = TraktSyncItemData


class TraktSyncItem(SyncItem):

    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'trakt_slug', 'premiered', 'year', 'title', 'status', 'country', 'certification', 'runtime',
        'trakt_rating', 'trakt_votes',
    )

    def get_data(self):
        return TraktSyncItemConstructor(self.meta, self.keys, self.item_type).data
