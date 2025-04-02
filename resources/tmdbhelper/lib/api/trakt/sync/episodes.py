#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.api.trakt.sync.database import SyncDataBase
from tmdbhelper.lib.addon.thread import ParallelThread
from jurialmunkey.locker import MutexPropLock


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

    slugs_columns = {
        'slug': {
            'data': 'TEXT',
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
        'slug': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(slug)': {
            'data': 'REFERENCES slugs(slug)',
            'sync': None
        }
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
        'slug': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(slug)': {
            'data': 'REFERENCES slugs(slug)',
            'sync': None
        }
    }

    @property
    def database_tables(self):
        return {
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
            'slugs': self.slugs_columns,
            'seasons': self.seasons_columns,
            'episodes': self.episodes_columns,
        }


class SyncTraktAPIData:

    table = None  # Table in database
    conditions = ()  # WHERE conditions
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
            self.conditions, self.values, self.keys, self.table,
            self.get_online_data
        )


class SyncTraktAPISeasonsData(SyncTraktAPIData):

    table = 'seasons'
    conditions = ('slug=?',)
    keys = ('tmdb_id', 'season_number', 'slug', )

    def __init__(self, ci_synctraktapi, tmdb_id):
        self.ci_synctraktapi = ci_synctraktapi
        self.tmdb_id = tmdb_id

    @cached_property
    def values(self):
        return (self.slug, )

    @cached_property
    def online_data_args(self):
        return ('shows', self.slug, 'seasons', )

    @property
    def data_cond(self):
        return self.slug

    @cached_property
    def slug(self):
        return self.ci_synctraktapi.get_slug(self.tmdb_id)

    def get_item_id(self, season_number):
        return f'tv.{self.tmdb_id}.{season_number}'

    def get_online_data(self):
        if not self.online_data:
            return
        return {self.get_item_id(i['number']): (self.tmdb_id, i['number'], self.slug, ) for i in self.online_data}


class SyncTraktAPISeasonEpisodesData(SyncTraktAPISeasonsData):

    table = 'episodes'
    conditions = ('slug=?', 'season_number=?', )
    keys = ('tmdb_id', 'season_number', 'episode_number', 'slug', )

    def __init__(self, ci_synctraktapi, tmdb_id, season_number):
        self.ci_synctraktapi = ci_synctraktapi
        self.tmdb_id = tmdb_id
        self.season_number = season_number

    @cached_property
    def values(self):
        return (self.slug, self.season_number, )

    @cached_property
    def online_data_args(self):
        return ('shows', self.slug, 'seasons', self.season_number)

    def get_item_id(self, episode_number):
        return f'tv.{self.tmdb_id}.{self.season_number}.{episode_number}'

    def get_online_data(self):
        if not self.online_data:
            return
        return {self.get_item_id(i['number']): (self.tmdb_id, self.season_number, i['number'], self.slug, ) for i in self.online_data}


class SyncTraktAPI:
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

    def get_slug(self, tmdb_id):
        return self.use_cached(
            f'tv.{tmdb_id}', 'slug', 'slugs',
            self.get_id, tmdb_id, 'tmdb', 'show', 'slug')

    def get_cached(self, item_id, key, table):
        data = self.cache.get_values(item_id, keys=(key, ), table=table)
        return data[0] if data else None

    def set_cached(self, item_id, key, table, data):
        if not data:
            return
        key_value_pair = (key, data,)
        self.cache.set_values(item_id, key_value_pairs=(key_value_pair, ), table=table)
        return data

    def use_cached(self, item_id, key, table, func, *args, **kwargs):
        data = self.get_cached(item_id, key, table)
        if not data:
            data = self.set_cached(item_id, key, table, func(*args, **kwargs))
        return data

    def set_cached_many(self, keys, table, data):
        if not data:
            return
        self.cache.set_many_values(keys=keys, data=data, table=table)
        return [v for _, v in data.items()]

    def use_cached_many(self, conditions, values, keys, table, func, *args, **kwargs):
        data = self.cache.get_list_values(conditions, values, keys, table)
        if not data:
            data = self.set_cached_many(keys, table, func(*args, **kwargs))
        return data

    def get_seasons_data(self, tmdb_id, slug=None):
        sync = SyncTraktAPISeasonsData(self, tmdb_id)
        if slug:
            sync.slug = slug
        return sync.data

    def get_episodes_data(self, tmdb_id, season_number, slug=None):
        sync = SyncTraktAPISeasonEpisodesData(self, tmdb_id, season_number)
        if slug:
            sync.slug = slug
        return sync.data


class SyncShowSeasonEpisodesData(SyncTraktAPI):
    def __init__(self, class_instance_sync_episodes_data, tmdb_id, slug, season_number):
        self.tmdb_id = tmdb_id
        self.slug = slug
        self.season_number = season_number
        self.cache = class_instance_sync_episodes_data.cache
        self.class_instance_trakt_api = class_instance_sync_episodes_data.class_instance_trakt_api
        self.class_instance_sync_episodes_data = class_instance_sync_episodes_data

    def get_episode(self, episode_number):
        if self.check_value(episode_number):  # Only get episodes we dont already have in cache
            return
        return self.get_response_json('shows', self.slug, 'seasons', self.season_number, 'episodes', episode_number, extended='full')

    @cached_property
    def season_episodes(self):
        return self.get_episodes_data(self.tmdb_id, self.season_number, self.slug)

    @staticmethod
    def get_name(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    def check_value(self, episode_number):
        return self.cache.get_values(self.get_name('tv', self.tmdb_id, self.season_number, episode_number), ('id', ))

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
    def slug(self):
        return self.get_slug(self.tmdb_id)

    @cached_property
    def seasons(self):
        if not self.slug:
            return
        return self.get_seasons_data(self.tmdb_id, self.slug)

    @cached_property
    def episodes(self):
        with ParallelThread(self.seasons, self.get_episodes) as pt:
            item_queue = pt.queue
        return [episode for season in item_queue if season for episode in season if episode]

    def get_episodes(self, season_object):
        season_number = season_object[SyncTraktAPISeasonsData.keys.index('season_number')]
        sync = SyncShowSeasonEpisodesData(self.class_instance_sync_episodes_data, self.tmdb_id, self.slug, season_number)
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

    cache_filename = 'TraktEpisodes.db'

    def __init__(self, class_instance_trakt_api):
        self.class_instance_trakt_api = class_instance_trakt_api  # The TraktAPI object sync called from

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
        return self.cache.get_values(self.get_name('tv', tmdb_id, season, episode), keys)

    def get_value(self, tmdb_id, season, episode, key=None):
        data = self.get_values(tmdb_id, season, episode, keys=(key,))
        return data[0] if data else None

    @cached_property
    def keys(self):
        return tuple([k for k in self.cache.simplecache_columns.keys()])

    def mutexlock(func):
        def wrapper(self, *args, **kwargs):
            filename = f'{self.cache._db_file}.{func.__name__}.{args}.lockfile'
            with MutexPropLock(filename, timeout=300, kodi_log=self.cache.kodi_log) as mutex_lock:
                if mutex_lock.lockstate == -1:  # Abort or Timeout
                    return
                return func(self, *args, **kwargs)
        return wrapper

    @mutexlock
    def sync_single_episode(self, tmdb_id, season, episode):
        if self.cache.get_values(self.get_name('tv', tmdb_id, season, episode), ('id', )):
            return
        self.sync_func_single_episode(tmdb_id, season, episode)

    @mutexlock
    def sync_all_episodes(self, tmdb_id):
        data = {}
        sync = SyncShowEpisodesData(self, tmdb_id)
        for item in sync.episodes:
            item_data = SyncEpisodeItemData(item, tmdb_id)
            data[item_data.item_id] = [getattr(item_data, k) for k in self.keys]
        self.cache.set_many_values(self.keys, data)
        return data

    def sync_func_single_episode(self, tmdb_id, season, episode):
        slug = self.get_slug(tmdb_id)
        if not slug:
            return
        item = self.get_response_json('shows', slug, 'seasons', season, 'episodes', episode, extended='full')
        if not item:
            return
        data = SyncEpisodeItemData(item, tmdb_id)
        self.cache.set_many_values(self.keys, {data.item_id: [getattr(data, k) for k in self.keys]})
