#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.database import DataBase


class ItemDetailsDataBase(DataBase):

    simplecache_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'mediatype': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'season': {
            'data': 'INTEGER',
            'sync': None
        },
        'episode': {
            'data': 'INTEGER',
            'sync': None
        },
        'year': {
            'data': 'INTEGER',
            'sync': None
        },
        'mpaa': {
            'data': 'TEXT',
            'sync': None
        },
        'plot': {
            'data': 'TEXT',
            'sync': None
        },
        'plotoutline': {
            'data': 'TEXT',
            'sync': None
        },
        'title': {
            'data': 'TEXT',
            'sync': None
        },
        'originaltitle': {
            'data': 'TEXT',
            'sync': None
        },
        'duration': {
            'data': 'INTEGER',
            'sync': None
        },
        'tagline': {
            'data': 'TEXT',
            'sync': None
        },
        'tvshowtitle': {
            'data': 'TEXT',
            'sync': None
        },
        'status': {
            'data': 'TEXT',
            'sync': None
        },
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'set': {
            'data': 'TEXT',
            'sync': None
        },
        'trailer': {
            'data': 'TEXT',
            'sync': None
        },
    }

    ratings_awards_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'top250': {
            'data': 'INTEGER',
            'sync': None
        },
        'tmdb_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'tmdb_votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'imdb_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'imdb_votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_usermeter': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_userreviews': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_reviewtotal': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_reviewsfresh': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_reviewsrotten': {
            'data': 'INTEGER',
            'sync': None
        },
        'rottentomatoes_consensus': {
            'data': 'TEXT',
            'sync': None
        },
        'metacritic_rating': {
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
        'letterboxd_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'letterboxd_votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'mdblist_rating': {
            'data': 'INTEGER',
            'sync': None
        },
        'mdblist_votes': {
            'data': 'INTEGER',
            'sync': None
        },
        'awards': {
            'data': 'TEXT',
            'sync': None
        },
        'goldenglobe_wins': {
            'data': 'INTEGER',
            'sync': None
        },
        'goldenglobe_nominations': {
            'data': 'INTEGER',
            'sync': None
        },
        'oscar_wins': {
            'data': 'INTEGER',
            'sync': None
        },
        'oscar_nominations': {
            'data': 'INTEGER',
            'sync': None
        },
        'award_wins': {
            'data': 'INTEGER',
            'sync': None
        },
        'award_nominations': {
            'data': 'INTEGER',
            'sync': None
        },
        'emmy_wins': {
            'data': 'INTEGER',
            'sync': None
        },
        'emmy_nominations': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    kodi_db_ids_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'dbid': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    genre_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    country_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    studio_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'icon': {
            'data': 'TEXT',
            'sync': None
        },
        'monoicon': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    crew_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'role': {
            'data': 'TEXT',
            'sync': None
        },
        'department': {
            'data': 'TEXT',
            'sync': None
        },
        'thumb': {
            'data': 'TEXT',
            'sync': None
        },
        'order': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    cast_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'sync': None
        },
        'role': {
            'data': 'TEXT',
            'sync': None
        },
        'thumb': {
            'data': 'TEXT',
            'sync': None
        },
        'order': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    custom_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'key': {
            'data': 'TEXT',
            'sync': None
        },
        'value': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    artwork_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'key': {
            'data': 'TEXT',
            'sync': None
        },
        'value': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    unique_id_columns = {
        'id': {
            'data': 'TEXT',
            'sync': None
        },
        'key': {
            'data': 'TEXT',
            'sync': None
        },
        'value': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    expiry_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'expiry': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES simplecache(id)',
            'sync': None
        }
    }

    @property
    def database_tables(self):
        return {
            'simplecache': self.simplecache_columns,
            'ratings_awards': self.ratings_awards_columns,
            'kodi_db_ids': self.kodi_db_ids_columns,
            'genre': self.genre_columns,
            'country': self.country_columns,
            'studio': self.studio_columns,
            'crew': self.crew_columns,
            'cast': self.cast_columns,
            'custom': self.custom_columns,
            'artwork': self.artwork_columns,
            'unique_id': self.unique_id_columns,
            'expiry': self.expiry_columns,
        }

    def create_database_execute(self, connection):
        for table, columns in self.database_tables.items():
            query = 'CREATE TABLE IF NOT EXISTS {table}({data})'
            query = query.format(table=table, data=', '.join([f'{k} {v["data"]}' for k, v in columns.items()]))
            connection.execute(query)
