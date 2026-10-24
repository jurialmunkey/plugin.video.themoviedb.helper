#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property


class SyncItemConstructorBase:

    item_constructor = None

    def __init__(self, constructor, item):
        self.constructor = constructor
        self.item = item

    @property
    def keys(self):
        return self.constructor.keys

    @property
    def item_data_class(self):
        return self.constructor.item_data_class

    @cached_property
    def item_type(self):
        return self.item.get('type') or self.constructor.item_type

    @cached_property
    def item_data(self):
        return self.item_data_class(self.item, self.item_type)

    @cached_property
    def meta(self):
        return tuple()  # if self.item_data.item_type != 'show':

    @cached_property
    def items(self):
        return [self.item_constructor(self, item) for item in self.meta]

    @cached_property
    def item_data_configured(self):
        return self.get_item_data_configured()

    def get_item_data_configured(self):
        item_data_configured = [getattr(self.item_data, k) for k in self.keys]
        return item_data_configured

    @cached_property
    def data(self):
        data = {k: v for i in self.items for k, v in i.data.items()}
        data[self.item_data.item_id] = self.item_data_configured
        return data


class SyncItemConstructorTV(SyncItemConstructorBase):
    @cached_property
    def watched_episodes(self):
        return self.get_watched_episodes()

    def get_watched_episodes(self):
        return self.get_watched_episodes_sum()

    def get_watched_episodes_sum(self):
        return sum((i.watched_episodes for i in self.items))

    def get_item_data_configured(self):
        self.item_data.watched_episodes = self.watched_episodes
        return super().get_item_data_configured()


class SyncItemConstructorEpisode(SyncItemConstructorTV):
    meta = None
    item_type = 'episode'
    items = tuple()

    @cached_property
    def reset_at(self):
        return self.constructor.constructor.item_data.reset_at  # Stored in show

    @cached_property
    def tmdb_id(self):
        return self.constructor.item_data.tmdb_id

    @cached_property
    def season_number(self):
        return self.constructor.season_number

    @cached_property
    def episode_number(self):
        return self.item['number']

    @cached_property
    def item_data(self):
        item_data = self.item_data_class(self.item, self.item_type)
        item_data.tmdb_id = self.tmdb_id
        item_data.season_number = self.season_number
        item_data.episode_number = self.episode_number
        return item_data

    def get_watched_episodes(self):
        if not self.item_data.last_watched_at:  # Havent watched it
            return 0
        if not self.reset_at:  # First play through so we count it
            return 1
        if self.item_data.last_watched_at > self.reset_at:  # On a rewatch only count after restarted watching
            return 1
        return 0  # Havent watched it yet on rewatch


class SyncItemConstructorSeason(SyncItemConstructorTV):
    item_type = 'season'
    item_constructor = SyncItemConstructorEpisode

    @cached_property
    def tmdb_id(self):
        return self.constructor.item_data.tmdb_id

    @cached_property
    def season_number(self):
        return self.item['number']

    @cached_property
    def item_data(self):
        item_data = self.item_data_class(self.item, self.item_type)
        item_data.tmdb_id = self.tmdb_id
        item_data.season_number = self.season_number
        return item_data

    def get_watched_episodes(self):
        return self.get_watched_episodes_sum() if self.season_number else 0  # Dont count specials

    @cached_property
    def meta(self):
        return self.item.get('episodes') or tuple()


class SyncItemConstructorShow(SyncItemConstructorTV):

    item_constructor = SyncItemConstructorSeason

    @cached_property
    def meta(self):
        return self.item.get('seasons') or tuple()  # if self.item_data.item_type != 'show':

    @cached_property
    def item_data(self):
        item_data = self.item_data_class(self.item, self.item_type)
        return item_data


class SyncItemConstructor:
    def __init__(self, meta, keys, item_type):
        self.meta = meta
        self.keys = keys
        self.item_type = item_type

    @cached_property
    def items(self):
        return [SyncItemConstructorShow(self, item) for item in self.meta]

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        return {
            k: v
            for d in (i.data for i in self.items)
            for k, v in d.items()
        }
