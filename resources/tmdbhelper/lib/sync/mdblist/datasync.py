#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.datasync import (
    SyncDataGetterAll,
    SyncDataGetterAllMoviesToWatch,
    SyncDataGetterAllShowsToWatch,
)


class MDbListSyncDataGetterShowWatchedCounts(SyncDataGetterAll):
    item_type = 'show'
    query_clauses = ('item_type=?', )
    clause_keys = ('id', )
    episode_conditions = 'episode.season_number>0'

    @property
    def query_values(self):
        return ('episode', self.item_type, )

    def get_keys(self):
        return (
            'id',
            '('
            'SELECT COUNT(*) FROM simplecache episode '
            'WHERE episode.item_type=? AND episode.plays>0 '
            'AND episode.tmdb_type=simplecache.tmdb_type '
            'AND episode.tmdb_id=simplecache.tmdb_id '
            f'AND {self.episode_conditions}'
            ') AS watched_episodes',
        )

    def get_items(self):
        # Called after watched sync; read stored data without recursively syncing it.
        return self.instance_syncdata.cache.get_list_values(keys=self.keys, values=self.query_values, conditions=self.clause)


class MDbListSyncDataGetterSeasonWatchedCounts(MDbListSyncDataGetterShowWatchedCounts):
    item_type = 'season'
    episode_conditions = 'episode.season_number>0 AND episode.season_number=simplecache.season_number'


class MDbListSyncDataGetterAllUnHiddenMoviesToWatch(SyncDataGetterAllMoviesToWatch):
    pass


class MDbListSyncDataGetterAllUnHiddenShowsToWatch(SyncDataGetterAllShowsToWatch):
    query_clauses = ('item_type=?', 'dropped_hidden_at IS NULL', )
    filter_keys = ('dropped_hidden_at', )


class MDbListSyncDataGetterAllUnHiddenShowsInProgress:
    additional_keys = ()

    def __init__(self, instance_syncdata):
        self.instance_syncdata = instance_syncdata

    @cached_property
    def parent_getter(self):
        return self.get_parent_getter()

    def get_parent_getter(self):
        sd = self.instance_syncdata.get_all_unhidden_shows_started_getter()
        sd.additional_keys = self.parent_additional_keys
        return sd

    @cached_property
    def keys(self):
        return self.get_keys()

    def get_keys(self):
        return self.parent_getter.keys

    @property
    def parent_additional_keys(self):
        return ('aired_episodes', 'watched_episodes', 'dropped_hidden_at', 'last_watched_at', *(self.additional_keys or ()))

    @cached_property
    def items(self):
        return self.get_items()

    def is_inprogress(self, item):
        if not item['aired_episodes']:
            return False
        if not item['watched_episodes']:
            return True
        if item['aired_episodes'] > item['watched_episodes']:
            return True
        return False

    def get_items(self):
        sd = self.parent_getter
        return [i for i in sd.items if self.is_inprogress(i)]
