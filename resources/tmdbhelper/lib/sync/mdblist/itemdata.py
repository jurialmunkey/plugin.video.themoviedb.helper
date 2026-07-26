#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.itemdata import SyncItemData, SyncItem


class MDbListSyncItemData(SyncItemData):  # TODO: FIXME

    # FIXME TODO
    rank = None
    notes = None
    season_number = None
    episode_number = None

    """
    tmdb_id
    """
    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_tmdb_id(self):
        return self.item['ids']['tmdb']

    """
    listed_at
    """
    @cached_property
    def listed_at(self):
        return self.get_listed_at()

    def get_listed_at(self):
        return self.item.get('watchlist_at') or self.item.get('listed_at')

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
        return self.item.get('release_year')

    """
    premiered
    """
    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        return self.item.get('release_date')

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
            item_data = MDbListSyncItemData(item, item.get('type') or self.item_type)  # TODO: FIXME CHECK if type valid for mdblist

            # Iterate through seasons data for watched type syncs where seasons/episodes presented as list
            # sync_seasons(item_data, item)  # TODO: FIXME

            # Set values to back to keys for database storage
            data[item_data.item_id] = [getattr(item_data, k) for k in self.keys]

        return data
