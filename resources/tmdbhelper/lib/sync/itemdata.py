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

    """
    id
    """
    @cached_property
    def id(self):
        return self.get_id()

    def get_id(self):
        return self.item.get('id')

    """
    progress
    """
    @cached_property
    def progress(self):
        return self.get_progress()

    def get_progress(self):
        return self.item.get('progress')

    """
    last_updated_at
    """
    @cached_property
    def last_updated_at(self):
        return self.get_last_updated_at()

    def get_last_updated_at(self):
        return self.item.get('last_updated_at') or self.item.get('updated_at')

    """
    paused_at
    """
    @cached_property
    def paused_at(self):
        return self.get_paused_at()

    def get_paused_at(self):
        return self.item.get('paused_at')

    """
    last_collected_at
    """
    @cached_property
    def last_collected_at(self):
        return self.get_last_collected_at()

    def get_last_collected_at(self):
        return self.item.get('last_collected_at') or self.item.get('collected_at')


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


class SyncItemConstructorBase:
    @cached_property
    def item_data_list(self):
        return self.get_item_data_list()

    def get_item_data_list(self):
        item_data_list = [self.get_item_data(item) for item in self.meta]
        return item_data_list

    @cached_property
    def item_data_list_all(self):
        return self.get_item_data_list_all()

    def get_item_data_list_all(self):
        item_data_list_all = []
        item_data_list_all.extend(self.item_data_list)
        for constructor in self.constructor_list:
            constructor.update_watched_episodes()
            item_data_list_all.extend(constructor.item_data_list_all)
        return item_data_list_all

    @cached_property
    def constructor_list(self):
        return self.get_constructor_list()

    def get_constructor_list(self):
        return tuple()

    @cached_property
    def watched_episodes(self):
        return self.get_watched_episodes()

    def get_watched_episodes(self):
        return sum([self.get_watched_increment(item_data) for item_data in self.item_data_list])

    def get_watched_increment(self, item_data):
        if not item_data.last_watched_at:
            return 0
        return 1

    def update_watched_episodes(self):
        self.item_data.watched_episodes = self.watched_episodes


class SyncItemConstructorSeasonEpisodes(SyncItemConstructorBase):
    def __init__(self, parent, item_data):
        self.parent = parent  # SyncItemConstructorShowSeasons
        self.item_data = item_data

    @property
    def item_data_class(self):
        return self.parent.item_data_class

    @property
    def reset_at(self):
        return self.parent.reset_at  # reset_at value of base show for restart watching

    @cached_property
    def meta(self):
        meta = self.item_data.item.get('episodes')
        return meta or tuple()

    def get_item_data(self, item):
        item_data = self.item_data_class(item, 'episode')
        item_data.tmdb_id = self.item_data.tmdb_id
        item_data.season_number = self.item_data.season_number
        item_data.episode_number = item["number"]
        return item_data

    def get_watched_increment(self, item_data):
        if not item_data.last_watched_at:
            return 0
        if not self.reset_at:  # If first watch through count the episode
            return 1
        if item_data.last_watched_at > self.reset_at:  # On a rewatch only count episodes since we restarted watching
            return 1
        return 0


class SyncItemConstructorShowSeasons(SyncItemConstructorBase):
    def __init__(self, parent, item_data):
        self.parent = parent  # SyncItemConstructor
        self.item_data = item_data

    @property
    def item_data_class(self):
        return self.parent.item_data_class

    @property
    def reset_at(self):
        return self.item_data.reset_at  # reset_at value of base show for restart watching

    @cached_property
    def meta(self):
        meta = self.item_data.item.get('seasons')
        return meta or tuple()

    def get_item_data(self, item):
        item_data = self.item_data_class(item, 'season')
        item_data.tmdb_id = self.item_data.tmdb_id
        item_data.season_number = item["number"]
        return item_data

    def get_watched_increment(self, item_data):
        if not item_data.watched_episodes:
            return 0
        if not item_data.season_number:  # Exclude counting special seasons in Show watched count
            return 0
        return item_data.watched_episodes

    def get_constructor_list(self):
        return tuple((
            SyncItemConstructorSeasonEpisodes(self, item_data)
            for item_data in self.item_data_list
        ))


class SyncItemConstructor(SyncItemConstructorBase):

    item_data_class = None  # TraktSyncItemData

    def __init__(self, meta, keys, item_type=None):
        self.meta = meta
        self.keys = keys
        self.item_type = item_type

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        data = {
            item_data.item_id: [getattr(item_data, k) for k in self.keys]
            for item_data in self.item_data_list_all
        }
        return data

    def get_item_data(self, item):
        return self.item_data_class(item, item.get('type') or self.item_type)

    def get_constructor_list(self):
        return tuple((
            SyncItemConstructorShowSeasons(self, item_data)
            for item_data in self.item_data_list
            if item_data.item_type == 'show'
        ))
