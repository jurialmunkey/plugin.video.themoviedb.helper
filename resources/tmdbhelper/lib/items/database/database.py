#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.dbdata import Database


class ItemDetailsDatabase(Database):
    cache_filename = 'ItemDetails.db'

    def __init__(self):
        super().__init__(filename=self.cache_filename)

    # DB version must be max of table_version
    database_version = 23

    database_changes = {
        21: (
            'ALTER TABLE tvshow ADD totalseasons INTEGER',
            'ALTER TABLE tvshow ADD totalepisodes INTEGER',
        ),
        22: (
            'DROP TABLE IF EXISTS studio',
            'DROP TABLE IF EXISTS network',
            'DROP TABLE IF EXISTS company',
        ),
        23: (
            'ALTER TABLE baseitem ADD datalevel INTEGER DEFAULT 0 NOT NULL',
            'ALTER TABLE ratings ADD datalevel INTEGER DEFAULT 0 NOT NULL',
        )
    }

    baseitem_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True
        },
        'mediatype': {
            'data': 'TEXT',
        },
        'expiry': {
            'data': 'INTEGER',
            'indexed': True
        },
        'datalevel': {
            'data': 'INTEGER DEFAULT 0 NOT NULL',
            'indexed': True
        },
    }

    movie_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True
        },
        'year': {
            'data': 'INTEGER',
            'indexed': True
        },
        'plot': {
            'data': 'TEXT',
        },
        'title': {
            'data': 'TEXT',
        },
        'originaltitle': {
            'data': 'TEXT',
        },
        'duration': {
            'data': 'INTEGER',
        },
        'tagline': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
            'indexed': True
        },
        'status': {
            'data': 'TEXT',
        },
        'rating': {
            'data': 'INTEGER',
            'indexed': True
        },
        'votes': {
            'data': 'INTEGER',
            'indexed': True
        },
        'popularity': {
            'data': 'INTEGER',
            'indexed': True
        },
        'collection_id': {
            'data': 'TEXT',
            'indexed': True
        },
    }

    tvshow_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True
        },
        'year': {
            'data': 'INTEGER',
            'indexed': True
        },
        'plot': {
            'data': 'TEXT',
        },
        'title': {
            'data': 'TEXT',
        },
        'originaltitle': {
            'data': 'TEXT',
        },
        'duration': {
            'data': 'INTEGER',
        },
        'tagline': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
            'indexed': True
        },
        'status': {
            'data': 'TEXT',
        },
        'rating': {
            'data': 'INTEGER',
            'indexed': True
        },
        'votes': {
            'data': 'INTEGER',
            'indexed': True
        },
        'popularity': {
            'data': 'INTEGER',
            'indexed': True
        },
        'next_episode_to_air_id': {
            'data': 'TEXT',
        },
        'totalseasons': {
            'data': 'INTEGER',
        },
        'totalepisodes': {
            'data': 'INTEGER',
        },
    }

    season_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
        },
        'season': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
            'indexed': True
        },
        'plot': {
            'data': 'TEXT',
        },
        'title': {
            'data': 'TEXT',
        },
        'originaltitle': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
            'indexed': True
        },
        'status': {
            'data': 'TEXT',
        },
        'rating': {
            'data': 'INTEGER',
            'indexed': True
        },
        'votes': {
            'data': 'INTEGER',
            'indexed': True
        },
        'popularity': {
            'data': 'INTEGER',
            'indexed': True
        },
        'tvshow_id': {
            'data': 'TEXT',
            'foreign_key': 'tvshow(id)',
            'indexed': True
        },
    }

    episode_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
        },
        'episode': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
            'indexed': True
        },
        'plot': {
            'data': 'TEXT',
        },
        'title': {
            'data': 'TEXT',
        },
        'originaltitle': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
            'indexed': True
        },
        'duration': {
            'data': 'INTEGER',
        },
        'status': {
            'data': 'TEXT',
        },
        'rating': {
            'data': 'INTEGER',
            'indexed': True
        },
        'votes': {
            'data': 'INTEGER',
            'indexed': True
        },
        'popularity': {
            'data': 'INTEGER',
            'indexed': True
        },
        'season_id': {
            'data': 'TEXT',
            'foreign_key': 'season(id)',
            'indexed': True
        },
        'tvshow_id': {
            'data': 'TEXT',
            'foreign_key': 'tvshow(id)',
            'indexed': True
        },
    }

    collection_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True,
            'foreign_key': 'baseitem(id)',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True
        },
        'plot': {
            'data': 'TEXT',
        },
        'title': {
            'data': 'TEXT',
        },
        'poster': {
            'data': 'TEXT',
        },
        'fanart': {
            'data': 'TEXT',
        },
    }

    ratings_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
        },
        'top250': {
            'data': 'INTEGER',
        },
        'tmdb_rating': {
            'data': 'INTEGER',
        },
        'tmdb_votes': {
            'data': 'INTEGER',
        },
        'imdb_rating': {
            'data': 'INTEGER',
        },
        'imdb_votes': {
            'data': 'INTEGER',
        },
        'rottentomatoes_rating': {
            'data': 'INTEGER',
        },
        'rottentomatoes_usermeter': {
            'data': 'INTEGER',
        },
        'rottentomatoes_userreviews': {
            'data': 'INTEGER',
        },
        'rottentomatoes_reviewstotal': {
            'data': 'INTEGER',
        },
        'rottentomatoes_reviewsfresh': {
            'data': 'INTEGER',
        },
        'rottentomatoes_reviewsrotten': {
            'data': 'INTEGER',
        },
        'rottentomatoes_consensus': {
            'data': 'TEXT',
        },
        'metacritic_rating': {
            'data': 'INTEGER',
        },
        'trakt_rating': {
            'data': 'INTEGER',
        },
        'trakt_votes': {
            'data': 'INTEGER',
        },
        'letterboxd_rating': {
            'data': 'INTEGER',
        },
        'letterboxd_votes': {
            'data': 'INTEGER',
        },
        'mdblist_rating': {
            'data': 'INTEGER',
        },
        'mdblist_votes': {
            'data': 'INTEGER',
        },
        'awards': {
            'data': 'TEXT',
        },
        'goldenglobe_wins': {
            'data': 'INTEGER',
        },
        'goldenglobe_nominations': {
            'data': 'INTEGER',
        },
        'oscar_wins': {
            'data': 'INTEGER',
        },
        'oscar_nominations': {
            'data': 'INTEGER',
        },
        'award_wins': {
            'data': 'INTEGER',
        },
        'award_nominations': {
            'data': 'INTEGER',
        },
        'emmy_wins': {
            'data': 'INTEGER',
        },
        'emmy_nominations': {
            'data': 'INTEGER',
        },
        'expiry': {
            'data': 'INTEGER',
            'indexed': True
        },
        'datalevel': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    person_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True,
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True,
        },
        'name': {
            'data': 'TEXT',
        },
        'thumb': {
            'data': 'TEXT',
        },
        'known_for_department': {
            'data': 'TEXT',
        },
        'gender': {
            'data': 'INTEGER',
        },
        'biography': {
            'data': 'TEXT',
        },
        'birthday': {
            'data': 'TEXT',
        },
        'deathday': {
            'data': 'TEXT',
        },
        'also_known_as': {
            'data': 'TEXT',
        },
        'place_of_birth': {
            'data': 'TEXT',
        },
        'popularity': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    certification_columns = {
        'name': {
            'data': 'TEXT',
        },
        'iso_country': {
            'data': 'TEXT',
            'unique': True,
            'indexed': True,
        },
        'iso_language': {
            'data': 'TEXT',
            'unique': True
        },
        'release_date': {
            'data': 'TEXT',
            'unique': True,
            'indexed': True,
        },
        'release_type': {
            'data': 'TEXT',
            'unique': True,
            'indexed': True,
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    video_columns = {
        'name': {
            'data': 'TEXT',
        },
        'iso_country': {
            'data': 'TEXT',
            'indexed': True,
        },
        'iso_language': {
            'data': 'TEXT',
            'indexed': True,
        },
        'release_date': {
            'data': 'TEXT',
            'indexed': True,
        },
        'key': {
            'data': 'TEXT',
        },
        'path': {
            'data': 'TEXT',
        },
        'content': {
            'data': 'TEXT',
            'indexed': True,
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
        },
    }

    genre_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    country_columns = {
        'name': {
            'data': 'TEXT',
        },
        'iso_country': {
            'data': 'TEXT',
            'unique': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    studio_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True,
            'foreign_key': 'company(tmdb_id)',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    network_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True,
            'foreign_key': 'broadcaster(tmdb_id)',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    company_columns = {
        'tmdb_id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT',
        },
        'logo': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
    }

    broadcaster_columns = {
        'tmdb_id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'name': {
            'data': 'TEXT',
        },
        'logo': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
    }

    crewmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'role': {
            'data': 'TEXT',
            'unique': True
        },
        'department': {
            'data': 'TEXT',
            'unique': True
        },
        'appearances': {
            'data': 'INTEGER',
            'indexed': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    castmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'indexed': True,
            'unique': True
        },
        'role': {
            'data': 'TEXT',
            'unique': True
        },
        'ordering': {
            'data': 'INTEGER',
            'indexed': True
        },
        'appearances': {
            'data': 'INTEGER',
            'indexed': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    custom_columns = {
        'key': {
            'data': 'TEXT',
        },
        'value': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True
        },
    }

    provider_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'foreign_key': 'service(tmdb_id)',
            'unique': True
        },
        'availability': {
            'data': 'TEXT',
            'indexed': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True,
            'unique': True
        },
    }

    service_columns = {
        'tmdb_id': {
            'data': 'INTEGER PRIMARY KEY',
            'indexed': True
        },
        'display_priority': {
            'data': 'INTEGER',
            'indexed': True
        },
        'name': {
            'data': 'TEXT',
        },
        'iso_country': {
            'data': 'TEXT',
            'indexed': True
        },
        'logo': {
            'data': 'TEXT',
        },
    }

    art_columns = {
        'aspect_ratio': {
            'data': 'INTEGER',
        },
        'quality': {
            'data': 'INTEGER',
        },
        'iso_language': {
            'data': 'TEXT',
            'indexed': True
        },
        'icon': {
            'data': 'TEXT',
        },
        'type': {
            'data': 'TEXT',
        },
        'extension': {
            'data': 'TEXT',
        },
        'rating': {
            'data': 'INTEGER',
            'indexed': True
        },
        'votes': {
            'data': 'INTEGER',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True
        },
    }

    fanart_tv_columns = {
        'icon': {
            'data': 'TEXT',
        },
        'iso_language': {
            'data': 'TEXT',
            'indexed': True
        },
        'likes': {
            'data': 'INTEGER',
            'indexed': True
        },
        'quality': {
            'data': 'INTEGER',
        },
        'type': {
            'data': 'TEXT',
        },
        'extension': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True
        },
    }

    unique_id_columns = {
        'key': {
            'data': 'TEXT',
        },
        'value': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'indexed': True
        },
    }

    simplecache_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True,
            'sync': None
        },
        'item_type': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_type': {
            'data': 'TEXT',
            'sync': None,
            'indexed': True
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None,
            'indexed': True
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
            'sync': None,
            'indexed': True
        },
        'year': {
            'data': 'INTEGER',
            'sync': None,
            'indexed': True
        },
        'title': {
            'data': 'TEXT',
            'sync': None
        },
        'status': {
            'data': 'TEXT',
            'sync': None,
            'indexed': True
        },
        'country': {
            'data': 'TEXT',
            'sync': None,
            'indexed': True
        },
        'certification': {
            'data': 'TEXT',
            'sync': None,
            'indexed': True
        },
        'runtime': {
            'data': 'INTEGER',
            'sync': None,
            'indexed': True
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
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', ),
            'indexed': True
        },
        'aired_episodes': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', ),
            'indexed': True
        },
        'watched_episodes': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', ),
            'indexed': True
        },
        'reset_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', )
        },
        'last_watched_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', ),
            'indexed': True
        },
        'last_updated_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatched', ),
            'indexed': True
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
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', ),
            'indexed': True
        },
        'watchlist_listed_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', ),
            'indexed': True
        },
        'watchlist_notes': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncWatchlist', )
        },
        'collection_last_collected_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncCollection', ),
            'indexed': True
        },
        'collection_last_updated_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncCollection', )
        },
        'playback_progress': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', ),
            'indexed': True
        },
        'playback_paused_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', ),
            'indexed': True
        },
        'playback_id': {
            'data': 'INTEGER',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncPlayback', ),
            'indexed': True
        },
        'progress_watched_hidden_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncHiddenProgressWatched', ),
            'indexed': True
        },
        'progress_collected_hidden_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncHiddenProgressCollected', ),
            'indexed': True
        },
        'calendar_hidden_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncHiddenCalendar', ),
            'indexed': True
        },
        'dropped_hidden_at': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncHiddenDropped', ),
            'indexed': True
        },
        'next_episode_id': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncNextEpisodes', ),
            'indexed': True
        },
        'upnext_episode_id': {
            'data': 'TEXT',
            'sync': ('tmdbhelper.lib.api.trakt.sync.datatype', 'SyncAllNextEpisodes', ),
            'indexed': True
        },
    }

    lactivities_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'indexed': True
        },
        'data': {
            'data': 'TEXT',
            'sync': None
        },
        'expiry': {
            'data': 'INTEGER',
            'indexed': True
        },
    }

    @property
    def database_tables(self):
        return {
            'baseitem': self.baseitem_columns,
            'collection': self.collection_columns,
            'movie': self.movie_columns,
            'tvshow': self.tvshow_columns,
            'season': self.season_columns,
            'episode': self.episode_columns,
            'ratings': self.ratings_columns,
            'person': self.person_columns,
            'genre': self.genre_columns,
            'country': self.country_columns,
            'studio': self.studio_columns,
            'company': self.company_columns,
            'network': self.network_columns,
            'broadcaster': self.broadcaster_columns,
            'video': self.video_columns,
            'certification': self.certification_columns,
            'crewmember': self.crewmember_columns,
            'castmember': self.castmember_columns,
            'provider': self.provider_columns,
            'service': self.service_columns,
            'custom': self.custom_columns,
            'art': self.art_columns,
            'fanart_tv': self.fanart_tv_columns,
            'unique_id': self.unique_id_columns,
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
        }
