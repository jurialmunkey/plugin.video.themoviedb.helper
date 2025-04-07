#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.database import DataBase


class SyncDataBase(DataBase):

    simplecache_columns = {
        'item_type': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_type': {
            'data': 'TEXT',
            'sync': None
        },
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
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'year': {
            'data': 'INTEGER',
            'sync': None
        },
        'title': {
            'data': 'TEXT',
            'sync': None
        },
        'status': {
            'data': 'TEXT',
            'sync': None
        },
        'country': {
            'data': 'TEXT',
            'sync': None
        },
        'certification': {
            'data': 'TEXT',
            'sync': None
        },
        'runtime': {
            'data': 'INTEGER',
            'sync': None
        },
        'trakt_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'trakt_votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'episode_type': {
            'data': 'TEXT',
            'sync': None
        },
        'plays': {
            'data': 'INTEGER DEFAULT 0',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'aired_episodes': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'watched_episodes': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'reset_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'last_watched_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'last_updated_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'rating': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncRatings', )
        },
        'rated_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncRatings', )
        },
        'favorites_rank': {
            'data': 'INTEGER DEFAULT 0',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncFavorites', )
        },
        'favorites_listed_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncFavorites', )
        },
        'favorites_notes': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncFavorites', )
        },
        'watchlist_rank': {
            'data': 'INTEGER DEFAULT 0',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', )
        },
        'watchlist_listed_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', )
        },
        'watchlist_notes': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', )
        },
        'collection_last_collected_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncCollection', )
        },
        'collection_last_updated_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncCollection', )
        },
        'playback_progress': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', )
        },
        'playback_paused_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', )
        },
        'playback_id': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', )
        },
        'hidden_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncHidden', )
        },
        'next_episode_id': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncNextEpisodes', )
        },
        'upnext_episode_id': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncAllNextEpisodes', )
        },
    }
