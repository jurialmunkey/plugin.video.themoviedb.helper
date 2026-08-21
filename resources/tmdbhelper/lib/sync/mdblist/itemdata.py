#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.itemdata import SyncItemData, SyncItem


class MDbListSyncItemData(SyncItemData):  # TODO: FIXME

    # FIXME TODO
    rank = None
    notes = None
    plays = 1
    last_updated_at = None
    aired_episodes = 0
    watched_episodes = 0
    reset_at = None

    """
    season_number
    """
    @cached_property
    def season_number(self):
        return self.get_season_number()

    def get_season_number(self):
        # TODO: CHECK MDBLIST SEASON TYPES
        # if self.item_type == 'season':
        #     return self.item["season"]["number"]
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
            return self.get_data_by_key('ids')['tmdb']
        except (AttributeError, KeyError, TypeError):
            pass

    """
    listed_at
    """
    @cached_property
    def listed_at(self):
        return self.get_listed_at()

    def get_listed_at(self):
        return self.item.get('watchlist_at') or self.item.get('listed_at')

    """
    helper getter for parent item
    """

    def get_data_by_key(self, key):
        try:
            return self.item[self.parent_item_type][key]
        except (AttributeError, KeyError, TypeError):
            pass
        try:
            return self.item[self.item_type][self.parent_item_type][key]
        except (AttributeError, KeyError, TypeError):
            pass
        try:
            return self.item[key]
        except (AttributeError, KeyError, TypeError):
            pass

    """
    title
    """
    @cached_property
    def title(self):
        return self.get_title()

    def get_title(self):
        return self.get_data_by_key('title')

    """
    year
    """
    @cached_property
    def year(self):
        return self.get_year()

    def get_year(self):
        return self.get_data_by_key('release_year') or self.get_data_by_key('year')

    """
    premiered
    """
    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        return self.get_data_by_key('release_date')

    """
    status
    """
    @cached_property
    def status(self):
        return self.get_status()

    def get_status(self):
        return self.get_data_by_key('status')

    """
    country
    """
    @cached_property
    def country(self):
        return self.get_country()

    def get_country(self):
        return self.get_data_by_key('country')

    """
    runtime
    """
    @cached_property
    def runtime(self):
        return self.get_runtime()

    def get_runtime(self):
        return self.get_data_by_key('runtime')

    """
    next_episode_object
    """
    @cached_property
    def next_episode_object(self):
        return self.get_next_episode_object()

    def get_next_episode_object(self):
        try:
            return self.item['next_episode']
        except (AttributeError, KeyError, TypeError):
            return

    """
    next_episode_id
    """
    @cached_property
    def next_episode_id(self):
        return self.get_next_episode_id()

    def get_next_episode_id(self):
        if not self.next_episode_object:
            return
        e_num = self.next_episode_object['episode']
        s_num = self.next_episode_object['season']
        return f'tv.{self.tmdb_id}.{s_num}.{e_num}'

    """
    next_episode_aired_at
    """
    @cached_property
    def next_episode_aired_at(self):
        return self.get_next_episode_aired_at()

    def get_next_episode_aired_at(self):
        if not self.next_episode_object:
            return
        air_date = self.next_episode_object['air_date']
        return f'{air_date}T00:00:00.000Z'  # No time from MDBList so set as 00:00 utc

    """
    last_watched_at
    """
    @cached_property
    def last_watched_at(self):
        return self.get_last_watched_at()

    def get_last_watched_at(self):
        return self.item.get('last_watched_at')


class MDbListSyncItem(SyncItem):

    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'year', 'title', 'premiered', 'status', 'country', 'runtime',
    )

    def __init__(self, item_type, meta, keys, key_prefix=None):
        self.meta = meta
        self.base_keys = keys
        self.item_type = item_type
        self.key_prefix = key_prefix

    @cached_property
    def data(self):
        return self.get_data()

    @property
    def additional_keys(self):
        return self._additional_keys

    @property
    def keys(self):
        return (*self.base_keys, *self.additional_keys)

    @property
    def base_table_keys(self):
        if not self.key_prefix:
            return self.base_keys
        return tuple([f'{self.key_prefix}_{k}' for k in self.base_keys])

    @property
    def table_keys(self):
        return (*self.base_table_keys, *self.additional_keys)

    def get_data(self):
        data = {}

        for item in self.meta:
            item_data = MDbListSyncItemData(item, item.get('type') or self.item_type)

            # Iterate through seasons data for watched type syncs where seasons/episodes presented as list
            # sync_seasons(item_data, item)  # TODO: FIXME DOES MDBLIST WORK LIKE THIS???

            # Set values to back to keys for database storage
            data[item_data.item_id] = [getattr(item_data, k) for k in self.keys]

        return data
