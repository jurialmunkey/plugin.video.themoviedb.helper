#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property


class SyncItemData:

    def __init__(self, item, item_type):
        self.item = item
        self.item_type = item_type

    """
    tmdb_type
    """
    @cached_property
    def tmdb_type(self):
        return self.get_tmdb_type()

    def get_tmdb_type(self):
        if self.item_type in ('show', 'season', 'episode',):
            return 'tv'
        if self.item_type == 'movie':
            return 'movie'

    """
    item_id
    """
    @cached_property
    def item_id(self):
        return self.get_item_id()

    def get_item_id(self):
        item_id = f'{self.tmdb_type}.{self.tmdb_id}'
        if self.item_type == 'season':
            return f'{item_id}.{self.season_number}'
        if self.item_type == 'episode':
            return f'{item_id}.{self.season_number}.{self.episode_number}'
        return item_id

    """
    parent_item_type
    """
    @cached_property
    def parent_item_type(self):
        return self.get_parent_item_type()

    def get_parent_item_type(self):
        if self.item_type in ('season', 'episode'):
            return 'show'
        return self.item_type


class SyncItem:

    _additional_keys = tuple()

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
        return {}
