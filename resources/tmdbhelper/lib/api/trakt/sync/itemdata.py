#!/usr/bin/python
# -*- coding: utf-8 -*-
from jurialmunkey.parser import LazyProperty


class SyncItemDataAttributes:
    """
    season_number
    """
    season_number = LazyProperty('season_number')

    def get_season_number(self):
        if self.item_type == 'season':
            return self.item["season"]["number"]
        if self.item_type == 'episode':
            return self.item["episode"]["season"]

    """
    episode_number
    """
    episode_number = LazyProperty('episode_number')

    def get_episode_number(self):
        if self.item_type == 'episode':
            return self.item["episode"]["number"]

    """
    tmdb_id
    """
    tmdb_id = LazyProperty('tmdb_id')

    def get_tmdb_id(self):
        return self.item[self.parent_item_type]['ids']['tmdb']

    """
    tmdb_type
    """
    tmdb_type = LazyProperty('tmdb_type')

    def get_tmdb_type(self):
        if self.item_type in ('show', 'season', 'episode',):
            return 'tv'
        if self.item_type == 'movie':
            return 'movie'

    """
    slug
    """
    slug = LazyProperty('slug')

    def get_slug(self):
        if self.parent_item_type not in self.item:
            return
        return self.item[self.parent_item_type]['ids']['slug']

    """
    item_id
    """
    item_id = LazyProperty('item_id')

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
    parent_item_type = LazyProperty('parent_item_type')

    def get_parent_item_type(self):
        if self.item_type in ('season', 'episode'):
            return 'show'
        return self.item_type

    """
    plays
    """
    plays = LazyProperty('plays')

    def get_plays(self):
        return self.item.get('plays')

    """
    last_watched_at
    """
    last_watched_at = LazyProperty('last_watched_at')

    def get_last_watched_at(self):
        return self.item.get('last_watched_at') or self.item.get('watched_at')

    """
    last_updated_at
    """
    last_updated_at = LazyProperty('last_updated_at')

    def get_last_updated_at(self):
        return self.item.get('last_updated_at') or self.item.get('updated_at')

    """
    last_collected_at
    """
    last_collected_at = LazyProperty('last_collected_at')

    def get_last_collected_at(self):
        return self.item.get('last_collected_at') or self.item.get('collected_at')

    """
    aired_episodes
    """
    aired_episodes = LazyProperty('aired_episodes')

    def get_aired_episodes(self):
        if 'show' not in self.item.keys():
            return
        return self.item['show'].get('aired_episodes')

    """
    reset_at
    """
    reset_at = LazyProperty('reset_at')

    def get_reset_at(self):
        return self.item.get('reset_at')

    """
    rating
    """
    rating = LazyProperty('rating')

    def get_rating(self):
        return self.item.get('rating')

    """
    rated_at
    """
    rated_at = LazyProperty('rated_at')

    def get_rated_at(self):
        return self.item.get('rated_at')

    """
    rank
    """
    rank = LazyProperty('rank')

    def get_rank(self):
        return self.item.get('rank')

    """
    listed_at
    """
    listed_at = LazyProperty('listed_at')

    def get_listed_at(self):
        return self.item.get('listed_at')

    """
    notes
    """
    notes = LazyProperty('notes')

    def get_notes(self):
        return self.item.get('notes')

    """
    episode_type
    """
    episode_type = LazyProperty('episode_type')

    def get_episode_type(self):
        return self.item.get('episode_type')

    """
    id
    """
    id = LazyProperty('id')

    def get_id(self):
        return self.item.get('id')

    """
    paused_at
    """
    paused_at = LazyProperty('paused_at')

    def get_paused_at(self):
        return self.item.get('paused_at')

    """
    progress
    """
    progress = LazyProperty('progress')

    def get_progress(self):
        return self.item.get('progress')

    """
    watched_episodes
    """
    watched_episodes = LazyProperty('watched_episodes')

    def get_watched_episodes(self):
        return

    """
    hidden_at
    """
    hidden_at = LazyProperty('hidden_at')

    def get_hidden_at(self):
        return self.item.get('hidden_at')

    """
    next_episode_id
    """
    next_episode_id = LazyProperty('next_episode_id')

    def get_next_episode_id(self):
        return self.item.get('next_episode_id')

    """
    upnext_episode_id
    """
    upnext_episode_id = LazyProperty('upnext_episode_id')

    def get_upnext_episode_id(self):
        return self.item.get('upnext_episode_id')

    """
    premiered
    """
    premiered = LazyProperty('premiered')

    def get_premiered(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('first_aired')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('released')

    """
    year
    """
    year = LazyProperty('year')

    def get_year(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('year')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('year')

    """
    title
    """
    title = LazyProperty('title')

    def get_title(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('title')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('title')

    """
    status
    """
    status = LazyProperty('status')

    def get_status(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('status')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('status')

    """
    country
    """
    country = LazyProperty('country')

    def get_country(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('country')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('country')

    """
    language
    """
    language = LazyProperty('language')

    def get_language(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('language')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('language')

    """
    certification
    """
    certification = LazyProperty('certification')

    def get_certification(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('certification')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('certification')

    """
    runtime
    """
    runtime = LazyProperty('runtime')

    def get_runtime(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('runtime')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('runtime')

    """
    trakt_rating
    """
    trakt_rating = LazyProperty('trakt_rating')

    def get_trakt_rating(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('rating')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('rating')

    """
    trakt_votes
    """
    trakt_votes = LazyProperty('trakt_votes')

    def get_trakt_votes(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('votes')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('votes')


class SyncItemData(SyncItemDataAttributes):

    def __init__(self, item, item_type):
        self.item = item
        self.item_type = item_type


class SyncItem:

    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'slug', 'premiered', 'year', 'title', 'status', 'country', 'certification', 'runtime',
        'trakt_rating', 'trakt_votes',
    )

    def __init__(self, item_type, meta, keys, key_prefix=None):
        self._meta = meta
        self._base_keys = keys
        self._item_type = item_type
        self._key_prefix = key_prefix

    @property
    def meta(self):
        return self._meta

    @property
    def item_type(self):
        return self._item_type

    @property
    def key_prefix(self):
        return self._key_prefix

    @property
    def base_keys(self):
        return self._base_keys

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

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = self.get_data()
            return self._data

    def get_data(self):
        data = {}

        def sync_episodes(season_data, season, item_data, item):
            episodes = season.get('episodes')
            if not episodes:
                return

            season_data.watched_episodes = 0
            for episode in episodes:
                episode_data = SyncItemData(episode, 'episode')
                episode_data.tmdb_id = season_data.tmdb_id
                episode_data.season_number = season_data.season_number
                episode_data.episode_number = episode["number"]

                # Count watched_episodes
                if episode_data.last_watched_at:
                    if not item_data.reset_at or episode_data.last_watched_at > item_data.reset_at:  # Only count episodes watched since we (re)started watching
                        season_data.watched_episodes += 1

                # Set values to back to keys for database storage
                data[episode_data.item_id] = [getattr(episode_data, k) for k in self.keys]

        def sync_seasons(item_data, item):
            if item_data.item_type != 'show':
                return
            seasons = item.get('seasons')
            if not seasons:
                return

            item_data.watched_episodes = 0
            for season in seasons:
                season_data = SyncItemData(season, 'season')
                season_data.tmdb_id = item_data.tmdb_id
                season_data.season_number = season["number"]

                # Iterate through episodes data
                sync_episodes(season_data, season, item_data, item)

                # Sum watched_episodes
                if season_data.watched_episodes:
                    if season_data.season_number and season_data.season_number != 0:  # Exclude special seasons
                        item_data.watched_episodes += season_data.watched_episodes

                # Set values to back to keys for database storage
                data[season_data.item_id] = [getattr(season_data, k) for k in self.keys]

        for item in self.meta:
            item_data = SyncItemData(item, item.get('type') or self.item_type)

            # Iterate through seasons data for watched type syncs where seasons/episodes presented as list
            sync_seasons(item_data, item)

            # Set values to back to keys for database storage
            data[item_data.item_id] = [getattr(item_data, k) for k in self.keys]

        return data
