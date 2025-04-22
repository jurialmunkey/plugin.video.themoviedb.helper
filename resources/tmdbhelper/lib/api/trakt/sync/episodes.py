#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.ftools import cached_property
from tmdbhelper.lib.files.database import DataBaseCache
from tmdbhelper.lib.api.trakt.sync.database import SyncDataBase
from tmdbhelper.lib.addon.thread import ParallelThread
from tmdbhelper.lib.files.locker import mutexlock_funcname


class SyncEpisodes(SyncDataBase):

    simplecache_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'season_number': {
            'data': 'INTEGER',
            'sync': None
        },
        'episode_number': {
            'data': 'INTEGER',
            'sync': None
        },
        'title': {
            'data': 'TEXT',
            'sync': None
        },
        'first_aired': {
            'data': 'TEXT',
            'sync': None
        },
        'updated_at': {
            'data': 'TEXT',
            'sync': None
        },
        'rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'comment_count': {
            'data': 'INTEGER',
            'sync': None
        },
        'episode_type': {
            'data': 'TEXT',
            'sync': None
        },
    }

    trakt_ids_columns = {
        'trakt_id': {
            'data': 'INTEGER',
            'sync': None
        },
    }

    seasons_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'season_number': {
            'data': 'INTEGER',
            'sync': None
        },
        'trakt_id': {
            'data': 'INTEGER',
            'sync': None
        },
    }

    episodes_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'season_number': {
            'data': 'INTEGER',
            'sync': None
        },
        'episode_number': {
            'data': 'INTEGER',
            'sync': None
        },
        'trakt_id': {
            'data': 'INTEGER',
            'sync': None
        },
    }

    @property
    def database_tables(self):
        return {
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
            'trakt_ids': self.trakt_ids_columns,
            'seasons': self.seasons_columns,
            'episodes': self.episodes_columns,
        }


class SyncTraktAPIData:

    table = None  # Table in database
    conditions = ''  # WHERE conditions
    values = ()  # WHERE conditions values for ?
    keys = ()  # Keys to lookup
    online_data_args = ()  # ARGS for get_response_json
    data_cond = False

    def __init__(self, ci_synctraktapi):
        self.ci_synctraktapi = ci_synctraktapi

    @property
    def online_data_cond(self):
        return self.data_cond

    @cached_property
    def online_data(self):
        if not self.online_data_cond:
            return
        return self.ci_synctraktapi.get_response_json(*self.online_data_args)

    def get_online_data(self):
        return

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        return self.ci_synctraktapi.use_cached_many(
            self.table, self.keys, self.values, self.conditions,
            self.get_online_data
        )


class SyncTraktAPISeasonsData(SyncTraktAPIData):

    table = 'seasons'
    conditions = 'trakt_id=?'
    keys = ('tmdb_id', 'season_number', 'trakt_id', )

    def __init__(self, ci_synctraktapi, tmdb_id):
        self.ci_synctraktapi = ci_synctraktapi
        self.tmdb_id = tmdb_id

    @cached_property
    def values(self):
        return (self.trakt_id, )

    @cached_property
    def online_data_args(self):
        return ('shows', self.trakt_id, 'seasons', )

    @property
    def data_cond(self):
        return self.trakt_id

    @cached_property
    def trakt_id(self):
        return self.ci_synctraktapi.get_trakt_id(self.tmdb_id)

    def get_item_id(self, season_number):
        return f'tv.{self.tmdb_id}.{season_number}'

    def get_online_data(self):
        if not self.online_data:
            return
        return {self.get_item_id(i['number']): (self.tmdb_id, i['number'], self.trakt_id, ) for i in self.online_data}


class SyncTraktAPISeasonEpisodesData(SyncTraktAPISeasonsData):

    table = 'episodes'
    conditions = 'trakt_id=? AND season_number=?'
    keys = ('tmdb_id', 'season_number', 'episode_number', 'trakt_id', )

    def __init__(self, ci_synctraktapi, tmdb_id, season_number):
        self.ci_synctraktapi = ci_synctraktapi
        self.tmdb_id = tmdb_id
        self.season_number = season_number

    @cached_property
    def values(self):
        return (self.trakt_id, self.season_number, )

    @cached_property
    def online_data_args(self):
        return ('shows', self.trakt_id, 'seasons', self.season_number)

    def get_item_id(self, episode_number):
        return f'tv.{self.tmdb_id}.{self.season_number}.{episode_number}'

    def get_online_data(self):
        if not self.online_data:
            return
        return {self.get_item_id(i['number']): (self.tmdb_id, self.season_number, i['number'], self.trakt_id, ) for i in self.online_data}


class SyncTraktAPI(DataBaseCache):
    def delete_response(self, *args, **kwargs):
        return self.class_instance_trakt_api.delete_response(*args, **kwargs)

    def post_response(self, *args, **kwargs):
        return self.class_instance_trakt_api.post_response(*args, **kwargs)

    def get_response_json(self, *args, **kwargs):
        return self.class_instance_trakt_api.get_response_json(*args, **kwargs)

    def get_request_lc(self, *args, **kwargs):
        return self.class_instance_trakt_api.get_request_lc(*args, **kwargs)

    def get_id(self, *args, **kwargs):
        return self.class_instance_trakt_api.get_id(*args, **kwargs)

    def get_trakt_id(self, tmdb_id):
        return self.use_cached(
            'trakt_ids', f'tv.{tmdb_id}', 'trakt_id',
            self.get_id, tmdb_id, 'tmdb', 'show', 'trakt')

    def get_seasons_data(self, tmdb_id, trakt_id=None):
        sync = SyncTraktAPISeasonsData(self, tmdb_id)
        if trakt_id:
            sync.trakt_id = trakt_id
        return sync.data

    def get_episodes_data(self, tmdb_id, season_number, trakt_id=None):
        sync = SyncTraktAPISeasonEpisodesData(self, tmdb_id, season_number)
        if trakt_id:
            sync.trakt_id = trakt_id
        return sync.data


class SyncShowSeasonEpisodesData(SyncTraktAPI):
    def __init__(self, class_instance_sync_episodes_data, tmdb_id, trakt_id, season_number):
        self.tmdb_id = tmdb_id
        self.trakt_id = trakt_id
        self.season_number = season_number
        self.cache = class_instance_sync_episodes_data.cache
        self.class_instance_trakt_api = class_instance_sync_episodes_data.class_instance_trakt_api
        self.class_instance_sync_episodes_data = class_instance_sync_episodes_data

    def get_episode(self, episode_number):
        if self.check_value(episode_number):  # Only get episodes we dont already have in cache
            return
        return self.get_response_json('shows', self.trakt_id, 'seasons', self.season_number, 'episodes', episode_number, extended='full')

    @cached_property
    def season_episodes(self):
        return self.get_episodes_data(self.tmdb_id, self.season_number, self.trakt_id)

    @staticmethod
    def get_name(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    def check_value(self, episode_number):
        return self.cache.get_values(item_id=self.get_name('tv', self.tmdb_id, self.season_number, episode_number), keys=('id', ))

    @cached_property
    def episodes(self):
        if not self.season_episodes:
            return
        x = SyncTraktAPISeasonEpisodesData.keys.index('episode_number')
        with ParallelThread([i[x] for i in self.season_episodes if i], self.get_episode) as pt:
            item_queue = pt.queue
        data = [episode for episode in item_queue if episode]
        return data


class SyncShowEpisodesData(SyncTraktAPI):
    def __init__(self, class_instance_sync_episodes_data, tmdb_id):
        self.tmdb_id = tmdb_id
        self.cache = class_instance_sync_episodes_data.cache
        self.class_instance_trakt_api = class_instance_sync_episodes_data.class_instance_trakt_api
        self.class_instance_sync_episodes_data = class_instance_sync_episodes_data

    @cached_property
    def trakt_id(self):
        return self.get_trakt_id(self.tmdb_id)

    @cached_property
    def seasons(self):
        if not self.trakt_id:
            return
        return self.get_seasons_data(self.tmdb_id, self.trakt_id)

    @cached_property
    def episodes(self):
        with ParallelThread(self.seasons, self.get_episodes) as pt:
            item_queue = pt.queue
        return [episode for season in item_queue if season for episode in season if episode]

    def get_episodes(self, season_object):
        season_number = season_object[SyncTraktAPISeasonsData.keys.index('season_number')]
        sync = SyncShowSeasonEpisodesData(self.class_instance_sync_episodes_data, self.tmdb_id, self.trakt_id, season_number)
        return sync.episodes

    def sync(self):
        if not self.seasons:
            return
        return self.episodes


class SyncEpisodeItemData:

    def __init__(self, item, tmdb_id):
        self.item = item
        self.tmdb_id = tmdb_id

    @property
    def item_id(self):
        return f'tv.{self.tmdb_id}.{self.season_number}.{self.episode_number}'

    @property
    def season_number(self):
        return self.item["season"]

    @property
    def episode_number(self):
        return self.item["number"]

    @property
    def title(self):
        return self.item["title"]

    @property
    def first_aired(self):
        return self.item["first_aired"]

    @property
    def updated_at(self):
        return self.item["updated_at"]

    @property
    def rating(self):
        return self.item["rating"]

    @property
    def votes(self):
        return self.item["votes"]

    @property
    def comment_count(self):
        return self.item["comment_count"]

    @property
    def episode_type(self):
        return self.item["episode_type"]


class SyncEpisodesData(SyncTraktAPI):

    cache_filename = 'TraktEpisodes_v2.db'

    def __init__(self, class_instance_trakt_api):
        self.class_instance_trakt_api = class_instance_trakt_api  # The TraktAPI object sync called from

    @property
    def mutex_lockname(self):
        return f'{self.cache._db_file}.lockfile'

    @cached_property
    def cache(self):
        return SyncEpisodes(filename=self.cache_filename)

    @cached_property
    def window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

    @staticmethod
    def get_name(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    def get_values(self, tmdb_id, season, episode, keys=None):
        self.sync_single_episode(tmdb_id, season, episode)
        return self.cache.get_values(item_id=self.get_name('tv', tmdb_id, season, episode), keys=keys)

    def get_value(self, tmdb_id, season, episode, key=None):
        data = self.get_values(tmdb_id, season, episode, keys=(key,))
        return data[0] if data else None

    @cached_property
    def keys(self):
        return tuple([k for k in self.cache.simplecache_columns.keys()])

    @mutexlock_funcname
    def sync_single_episode(self, tmdb_id, season, episode):
        if self.cache.get_values(item_id=self.get_name('tv', tmdb_id, season, episode), keys=('id', )):
            return
        self.sync_func_single_episode(tmdb_id, season, episode)

    @mutexlock_funcname
    def sync_all_episodes(self, tmdb_id):
        data = {}
        sync = SyncShowEpisodesData(self, tmdb_id)
        for item in sync.episodes:
            item_data = SyncEpisodeItemData(item, tmdb_id)
            data[item_data.item_id] = [getattr(item_data, k) for k in self.keys]
        self.cache.set_many_values(keys=self.keys, data=data)
        return data

    def sync_func_single_episode(self, tmdb_id, season, episode):
        trakt_id = self.get_trakt_id(tmdb_id)
        if not trakt_id:
            return
        item = self.get_response_json('shows', trakt_id, 'seasons', season, 'episodes', episode, extended='full')
        if not item:
            return
        data = SyncEpisodeItemData(item, tmdb_id)
        self.cache.set_many_values(keys=self.keys, data={data.item_id: [getattr(data, k) for k in self.keys]})
