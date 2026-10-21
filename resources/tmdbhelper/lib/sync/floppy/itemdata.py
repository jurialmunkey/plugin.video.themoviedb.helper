#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.itemdata import SyncItemData, SyncItem
from tmdbhelper.lib.sync.itemconf import SyncItemConstructor


class FloppySyncItemData(SyncItemData):
    """ Reads flat records configured by tmdbhelper.lib.sync.floppy.dataconf """

    rank = None  # Floppy does not rank items

    """
    season_number
    """
    @cached_property
    def season_number(self):
        return self.get_season_number()

    def get_season_number(self):
        return self.item.get('season_number')

    """
    episode_number
    """
    @cached_property
    def episode_number(self):
        return self.get_episode_number()

    def get_episode_number(self):
        return self.item.get('episode_number')

    """
    tmdb_id
    """
    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_tmdb_id(self):
        return self.item.get('tmdb_id')

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
        return self.item.get('last_watched_at')

    """
    watched_episodes
    """
    @cached_property
    def watched_episodes(self):
        return self.get_watched_episodes()

    def get_watched_episodes(self):
        return  # Calculated by SyncItemConstructor from nested episodes

    """
    aired_episodes
    """
    @cached_property
    def aired_episodes(self):
        return self.get_aired_episodes()

    def get_aired_episodes(self):
        """ Floppy reports aired episodes remaining so aired is watched plus remaining """
        try:
            return self.watched_episodes + self.item['episodes_left']
        except (KeyError, TypeError):
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
    title
    """
    @cached_property
    def title(self):
        return self.get_title()

    def get_title(self):
        return self.item.get('title')

    """
    year
    """
    @cached_property
    def year(self):
        return self.get_year()

    def get_year(self):
        return self.item.get('year')

    """
    premiered
    """
    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        return self.item.get('premiered')

    """
    status
    """
    @cached_property
    def status(self):
        return self.get_status()

    def get_status(self):
        return self.item.get('status')

    """
    country
    """
    @cached_property
    def country(self):
        return self.get_country()

    def get_country(self):
        return self.item.get('country')

    """
    runtime
    """
    @cached_property
    def runtime(self):
        return self.get_runtime()

    def get_runtime(self):
        return self.item.get('runtime')


class FloppySyncItemConstructor(SyncItemConstructor):
    item_data_class = FloppySyncItemData


class FloppySyncItem(SyncItem):

    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'year', 'title', 'premiered', 'status', 'country', 'runtime',
    )

    def get_data(self):
        return FloppySyncItemConstructor(self.meta, self.keys, self.item_type).data
