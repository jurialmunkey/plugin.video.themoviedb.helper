#!/usr/bin/python
# -*- coding: utf-8 -*-


BASEITEM_COLUMNS = {
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
    'fanart_tv': {
        'data': 'INTEGER DEFAULT 0 NOT NULL',
        'indexed': True
    },
    'language': {
        'data': 'TEXT',
    },
}

MOVIE_COLUMNS = {
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
}

TVSHOW_COLUMNS = {
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
    'last_episode_to_air_id': {
        'data': 'TEXT',
    },
    'totalseasons': {
        'data': 'INTEGER',
    },
    'totalepisodes': {
        'data': 'INTEGER',
    },
}

SEASON_COLUMNS = {
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

EPISODE_COLUMNS = {
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

BELONGS_COLUMNS = {
    'id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
}

COLLECTION_COLUMNS = {
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
}

RATINGS_COLUMNS = {
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
}

PERSON_COLUMNS = {
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

CERTIFICATION_COLUMNS = {
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

VIDEO_COLUMNS = {
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
        'unique': True,
    },
    'content': {
        'data': 'TEXT',
        'indexed': True,
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
}

GENRE_COLUMNS = {
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

COUNTRY_COLUMNS = {
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

STUDIO_COLUMNS = {
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

NETWORK_COLUMNS = {
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

COMPANY_COLUMNS = {
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

BROADCASTER_COLUMNS = {
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

CREWMEMBER_COLUMNS = {
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

CASTMEMBER_COLUMNS = {
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

CUSTOM_COLUMNS = {
    'key': {
        'data': 'TEXT',
        'unique': True
    },
    'value': {
        'data': 'TEXT',
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True
    },
}

PROVIDER_COLUMNS = {
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

SERVICE_COLUMNS = {
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

ART_COLUMNS = {
    'aspect_ratio': {
        'data': 'INTEGER',
    },
    'quality': {
        'data': 'INTEGER',
    },
    'iso_language': {
        'data': 'TEXT',
        'indexed': True,
    },
    'icon': {
        'data': 'TEXT',
        'unique': True,
    },
    'type': {
        'data': 'TEXT',
        'unique': True,
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
        'indexed': True,
        'unique': True,
    },
}

FANART_TV_COLUMNS = {
    'icon': {
        'data': 'TEXT',
        'unique': True,
    },
    'iso_language': {
        'data': 'TEXT',
        'indexed': True,
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
        'unique': True,
    },
    'extension': {
        'data': 'TEXT',
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
}

USER_ART_COLUMNS = {
    'type': {
        'data': 'TEXT',
        'unique': True,
    },
    'icon': {
        'data': 'TEXT',
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
}

UNIQUE_ID_COLUMNS = {
    'key': {
        'data': 'TEXT',
        'unique': True,
    },
    'value': {
        'data': 'TEXT',
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True,
    },
}

TRANSLATION_COLUMNS = {
    'iso_country': {
        'data': 'TEXT',
        'unique': True,
    },
    'iso_language': {
        'data': 'TEXT',
        'unique': True,
    },
    'plot': {
        'data': 'TEXT',
    },
    'title': {
        'data': 'TEXT',
    },
    'tagline': {
        'data': 'TEXT',
    },
    'parent_id': {
        'data': 'TEXT',
        'foreign_key': 'baseitem(id)',
        'indexed': True,
        'unique': True
    },
}

SIMPLECACHE_COLUMNS = {
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
    'trakt_slug': {
        'data': 'TEXT',
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
    'next_episode_aired_at': {
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

LACTIVITIES_COLUMNS = {
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
