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

    lactivities_columns = {
        'data': {'data': 'TEXT', 'sync': None}
    }


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


class SyncShowSeasonEpisodesData(SyncTraktAPI):
    def __init__(self, class_instance_sync_episodes_data, tmdb_id, slug, season):
        self.tmdb_id = tmdb_id
        self.slug = slug
        self.season = season
        self.cache = class_instance_sync_episodes_data.cache
        self.class_instance_trakt_api = class_instance_sync_episodes_data.class_instance_trakt_api
        self.class_instance_sync_episodes_data = class_instance_sync_episodes_data

    @cached_property
    def season_number(self):
        return self.season['number']

    def get_episode(self, episode):
        episode_number = episode['number']
        if self.check_value(episode_number):  # Only get episodes we dont already have in cache
            return
        return self.get_response_json('shows', self.slug, 'seasons', self.season_number, 'episodes', episode_number, extended='full')

    @cached_property
    def season_episodes(self):
        return self.get_request_lc('shows', self.slug, 'seasons', self.season_number)

    def check_value(self, episode_number):
        return self.cache.get_values(self.get_name('tv', self.tmdb_id, self.season_number, episode_number), ('id', ))

    @cached_property
    def episodes(self):
        if not self.season_episodes:
            return
        with ParallelThread(self.season_episodes, self.get_episode) as pt:
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
        return self.get_id(self.tmdb_id, 'tmdb', 'show', 'slug')

    @cached_property
    def seasons(self):
        if not self.slug:
            return
        return self.get_request_lc('shows', self.slug, 'seasons')

    @cached_property
    def episodes(self):
        with ParallelThread(self.seasons, self.get_episodes) as pt:
            item_queue = pt.queue
        return [episode for season in item_queue if season for episode in season if episode]

    def get_episodes(self, season):
        sync = SyncShowSeasonEpisodesData(self.class_instance_sync_episodes_data, self.tmdb_id, self.slug, season)
        return sync.episodes

    def sync(self):
        if not self.seasons:
            return
        return self.episodes


class SyncEpisodesData(SyncTraktAPI):

    cache_filename = 'TraktEpisodes.db'

    def __init__(self, class_instance_trakt_api):
        self.class_instance_trakt_api = class_instance_trakt_api  # The TraktAPI object sync called from

    @cached_property
    def cache(self):
        return self.get_cache()

    def get_cache(self):
        return SyncEpisodes(filename=self.cache_filename)

    @cached_property
    def window(self):
        return self.get_window()

    def get_window(self):
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

    def sync_func_single_episode(self, tmdb_id, season, episode):
        slug = self.get_id(tmdb_id, 'tmdb', 'show', 'slug')
        item = self.get_response_json('shows', slug, 'seasons', season, 'episodes', episode, extended='full')
        data = SyncEpisodeItemData(item, tmdb_id)
        self.cache.set_many_values(self.keys, {data.item_id: [getattr(data, k) for k in self.keys]})
