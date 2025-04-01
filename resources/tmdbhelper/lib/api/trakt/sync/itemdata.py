#!/usr/bin/python
# -*- coding: utf-8 -*-

class SyncItemDataAttributes:
    """
    season_number
    """
    @property
    def season_number(self):
        try:
            return self._season_number
        except AttributeError:
            self._season_number = self.get_season_number()
            return self._season_number

    @season_number.setter
    def season_number(self, value):
        self._season_number = value

    def get_season_number(self):
        if self.item_type == 'season':
            return self.item["season"]["number"]
        if self.item_type == 'episode':
            return self.item["episode"]["season"]

    """
    episode_number
    """
    @property
    def episode_number(self):
        try:
            return self._episode_number
        except AttributeError:
            self._episode_number = self.get_episode_number()
            return self._episode_number

    @episode_number.setter
    def episode_number(self, value):
        self._episode_number = value

    def get_episode_number(self):
        if self.item_type == 'episode':
            return self.item["episode"]["number"]

    """
    tmdb_id
    """
    @property
    def tmdb_id(self):
        try:
            return self._tmdb_id
        except AttributeError:
            self._tmdb_id = self.get_tmdb_id()
            return self._tmdb_id

    @tmdb_id.setter
    def tmdb_id(self, value):
        self._tmdb_id = value

    def get_tmdb_id(self):
        return self.item[self.parent_item_type]['ids']['tmdb']

    """
    tmdb_type
    """
    @property
    def tmdb_type(self):
        try:
            return self._tmdb_type
        except AttributeError:
            self._tmdb_type = self.get_tmdb_type()
            return self._tmdb_type

    @tmdb_type.setter
    def tmdb_type(self, value):
        self._tmdb_type = value

    def get_tmdb_type(self):
        if self.item_type in ('show', 'season', 'episode',):
            return 'tv'
        if self.item_type == 'movie':
            return 'movie'

    """
    slug
    """
    @property
    def slug(self):
        try:
            return self._slug
        except AttributeError:
            self._slug = self.get_slug()
            return self._slug

    @slug.setter
    def slug(self, value):
        self._slug = value

    def get_slug(self):
        if self.parent_item_type not in self.item:
            return
        return self.item[self.parent_item_type]['ids']['slug']

    """
    item_id
    """
    @property
    def item_id(self):
        try:
            return self._item_id
        except AttributeError:
            self._item_id = self.get_item_id()
            return self._item_id

    @item_id.setter
    def item_id(self, value):
        self._item_id = value

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
    @property
    def parent_item_type(self):
        try:
            return self._parent_item_type
        except AttributeError:
            self._parent_item_type = self.get_parent_item_type()
            return self._parent_item_type

    @parent_item_type.setter
    def parent_item_type(self, value):
        self._parent_item_type = value

    def get_parent_item_type(self):
        if self.item_type in ('season', 'episode'):
            return 'show'
        return self.item_type

    """
    plays
    """
    @property
    def plays(self):
        try:
            return self._plays
        except AttributeError:
            self._plays = self.get_plays()
            return self._plays

    @plays.setter
    def plays(self, value):
        self._plays = value

    def get_plays(self):
        return self.item.get('plays')

    """
    last_watched_at
    """
    @property
    def last_watched_at(self):
        try:
            return self._last_watched_at
        except AttributeError:
            self._last_watched_at = self.get_last_watched_at()
            return self._last_watched_at

    @last_watched_at.setter
    def last_watched_at(self, value):
        self._last_watched_at = value

    def get_last_watched_at(self):
        return self.item.get('last_watched_at') or self.item.get('watched_at')

    """
    last_updated_at
    """
    @property
    def last_updated_at(self):
        try:
            return self._last_updated_at
        except AttributeError:
            self._last_updated_at = self.get_last_updated_at()
            return self._last_updated_at

    @last_updated_at.setter
    def last_updated_at(self, value):
        self._last_updated_at = value

    def get_last_updated_at(self):
        return self.item.get('last_updated_at') or self.item.get('updated_at')

    """
    last_collected_at
    """
    @property
    def last_collected_at(self):
        try:
            return self._last_collected_at
        except AttributeError:
            self._last_collected_at = self.get_last_collected_at()
            return self._last_collected_at

    @last_collected_at.setter
    def last_collected_at(self, value):
        self._last_collected_at = value

    def get_last_collected_at(self):
        return self.item.get('last_collected_at') or self.item.get('collected_at')

    """
    aired_episodes
    """
    @property
    def aired_episodes(self):
        try:
            return self._aired_episodes
        except AttributeError:
            self._aired_episodes = self.get_aired_episodes()
            return self._aired_episodes

    @aired_episodes.setter
    def aired_episodes(self, value):
        self._aired_episodes = value

    def get_aired_episodes(self):
        if 'show' not in self.item.keys():
            return
        return self.item['show'].get('aired_episodes')

    """
    reset_at
    """
    @property
    def reset_at(self):
        try:
            return self._reset_at
        except AttributeError:
            self._reset_at = self.get_reset_at()
            return self._reset_at

    @reset_at.setter
    def reset_at(self, value):
        self._reset_at = value

    def get_reset_at(self):
        return self.item.get('reset_at')

    """
    rating
    """
    @property
    def rating(self):
        try:
            return self._rating
        except AttributeError:
            self._rating = self.get_rating()
            return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    def get_rating(self):
        return self.item.get('rating')

    """
    rated_at
    """
    @property
    def rated_at(self):
        try:
            return self._rated_at
        except AttributeError:
            self._rated_at = self.get_rated_at()
            return self._rated_at

    @rated_at.setter
    def rated_at(self, value):
        self._rated_at = value

    def get_rated_at(self):
        return self.item.get('rated_at')

    """
    rank
    """
    @property
    def rank(self):
        try:
            return self._rank
        except AttributeError:
            self._rank = self.get_rank()
            return self._rank

    @rank.setter
    def rank(self, value):
        self._rank = value

    def get_rank(self):
        return self.item.get('rank')

    """
    listed_at
    """
    @property
    def listed_at(self):
        try:
            return self._listed_at
        except AttributeError:
            self._listed_at = self.get_listed_at()
            return self._listed_at

    @listed_at.setter
    def listed_at(self, value):
        self._listed_at = value

    def get_listed_at(self):
        return self.item.get('listed_at')

    """
    notes
    """
    @property
    def notes(self):
        try:
            return self._notes
        except AttributeError:
            self._notes = self.get_notes()
            return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

    def get_notes(self):
        return self.item.get('notes')

    """
    episode_type
    """
    @property
    def episode_type(self):
        try:
            return self._episode_type
        except AttributeError:
            self._episode_type = self.get_episode_type()
            return self._episode_type

    @episode_type.setter
    def episode_type(self, value):
        self._episode_type = value

    def get_episode_type(self):
        return self.item.get('episode_type')

    """
    id
    """
    @property
    def id(self):
        try:
            return self._id
        except AttributeError:
            self._id = self.get_id()
            return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def get_id(self):
        return self.item.get('id')

    """
    paused_at
    """
    @property
    def paused_at(self):
        try:
            return self._paused_at
        except AttributeError:
            self._paused_at = self.get_paused_at()
            return self._paused_at

    @paused_at.setter
    def paused_at(self, value):
        self._paused_at = value

    def get_paused_at(self):
        return self.item.get('paused_at')

    """
    progress
    """
    @property
    def progress(self):
        try:
            return self._progress
        except AttributeError:
            self._progress = self.get_progress()
            return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value

    def get_progress(self):
        return self.item.get('progress')

    """
    watched_episodes
    """
    @property
    def watched_episodes(self):
        try:
            return self._watched_episodes
        except AttributeError:
            self._watched_episodes = self.get_watched_episodes()
            return self._watched_episodes

    @watched_episodes.setter
    def watched_episodes(self, value):
        self._watched_episodes = value

    def get_watched_episodes(self):
        return

    """
    hidden_at
    """
    @property
    def hidden_at(self):
        try:
            return self._hidden_at
        except AttributeError:
            self._hidden_at = self.get_hidden_at()
            return self._hidden_at

    @hidden_at.setter
    def hidden_at(self, value):
        self._hidden_at = value

    def get_hidden_at(self):
        return self.item.get('hidden_at')

    """
    next_episode_id
    """
    @property
    def next_episode_id(self):
        try:
            return self._next_episode_id
        except AttributeError:
            self._next_episode_id = self.get_next_episode_id()
            return self._next_episode_id

    @next_episode_id.setter
    def next_episode_id(self, value):
        self._next_episode_id = value

    def get_next_episode_id(self):
        return self.item.get('next_episode_id')

    """
    upnext_episode_id
    """
    @property
    def upnext_episode_id(self):
        try:
            return self._upnext_episode_id
        except AttributeError:
            self._upnext_episode_id = self.get_upnext_episode_id()
            return self._upnext_episode_id

    @upnext_episode_id.setter
    def upnext_episode_id(self, value):
        self._upnext_episode_id = value

    def get_upnext_episode_id(self):
        return self.item.get('upnext_episode_id')

    """
    premiered
    """
    @property
    def premiered(self):
        try:
            return self._premiered
        except AttributeError:
            self._premiered = self.get_premiered()
            return self._premiered

    @premiered.setter
    def premiered(self, value):
        self._premiered = value

    def get_premiered(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('first_aired')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('released')

    """
    year
    """
    @property
    def year(self):
        try:
            return self._year
        except AttributeError:
            self._year = self.get_year()
            return self._year

    @year.setter
    def year(self, value):
        self._year = value

    def get_year(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('year')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('year')

    """
    title
    """
    @property
    def title(self):
        try:
            return self._title
        except AttributeError:
            self._title = self.get_title()
            return self._title

    @title.setter
    def title(self, value):
        self._title = value

    def get_title(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('title')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('title')

    """
    status
    """
    @property
    def status(self):
        try:
            return self._status
        except AttributeError:
            self._status = self.get_status()
            return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def get_status(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('status')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('status')

    """
    country
    """
    @property
    def country(self):
        try:
            return self._country
        except AttributeError:
            self._country = self.get_country()
            return self._country

    @country.setter
    def country(self, value):
        self._country = value

    def get_country(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('country')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('country')

    """
    language
    """
    @property
    def language(self):
        try:
            return self._language
        except AttributeError:
            self._language = self.get_language()
            return self._language

    @language.setter
    def language(self, value):
        self._language = value

    def get_language(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('language')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('language')

    """
    certification
    """
    @property
    def certification(self):
        try:
            return self._certification
        except AttributeError:
            self._certification = self.get_certification()
            return self._certification

    @certification.setter
    def certification(self, value):
        self._certification = value

    def get_certification(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('certification')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('certification')

    """
    runtime
    """
    @property
    def runtime(self):
        try:
            return self._runtime
        except AttributeError:
            self._runtime = self.get_runtime()
            return self._runtime

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    def get_runtime(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('runtime')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('runtime')

    """
    trakt_rating
    """
    @property
    def trakt_rating(self):
        try:
            return self._trakt_rating
        except AttributeError:
            self._trakt_rating = self.get_trakt_rating()
            return self._trakt_rating

    @trakt_rating.setter
    def trakt_rating(self, value):
        self._trakt_rating = value

    def get_trakt_rating(self):
        if 'show' in self.item.keys():
            return self.item['show'].get('rating')
        if 'movie' in self.item.keys():
            return self.item['movie'].get('rating')

    """
    trakt_votes
    """
    @property
    def trakt_votes(self):
        try:
            return self._trakt_votes
        except AttributeError:
            self._trakt_votes = self.get_trakt_votes()
            return self._trakt_votes

    @trakt_votes.setter
    def trakt_votes(self, value):
        self._trakt_votes = value

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
