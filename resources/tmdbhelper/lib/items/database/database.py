#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.files.database import DataBaseCache, DataBase


class ItemDetailsDataBase(DataBase):

    baseitem_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'mediatype': {
            'data': 'TEXT',
            'sync': None
        },
        'expiry': {
            'data': 'TEXT',
            'sync': None
        },
    }

    movie_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'tmdb_id': {
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
        'status': {
            'data': 'TEXT',
            'sync': None
        },
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'trailer': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    tvshow_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'tmdb_id': {
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
        'status': {
            'data': 'TEXT',
            'sync': None
        },
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'trailer': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    season_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'season': {
            'data': 'INTEGER',
            'sync': None
        },
        'year': {
            'data': 'INTEGER',
            'sync': None
        },
        'plot': {
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
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'tvshow_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        },
        'FOREIGN KEY(tvshow_id)': {
            'data': 'REFERENCES tvshow(id)',
            'sync': None
        }
    }

    episode_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'plot': {
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
        'premiered': {
            'data': 'TEXT',
            'sync': None
        },
        'duration': {
            'data': 'INTEGER',
            'sync': None
        },
        'season_id': {
            'data': 'TEXT',
            'sync': None
        },
        'tvshow_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        },
        'FOREIGN KEY(tvshow_id)': {
            'data': 'REFERENCES tvshow(id)',
            'sync': None
        },
        'FOREIGN KEY(season_id)': {
            'data': 'REFERENCES season(id)',
            'sync': None
        }
    }

    ratings_columns = {
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
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }

    }

    kodi_dbid_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'dbid': {
            'data': 'INTEGER',
            'sync': None
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    genre_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    country_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
            'sync': None
        },
        'name': {
            'data': 'TEXT',
            'sync': None
        },
        'iso': {
            'data': 'TEXT',
            'sync': None
        },
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    studio_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'country': {
            'data': 'TEXT',
            'sync': None
        },
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    network_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'country': {
            'data': 'TEXT',
            'sync': None
        },
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    crew_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'ordering': {
            'data': 'INTEGER',
            'sync': None
        },
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    cast_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'ordering': {
            'data': 'INTEGER',
            'sync': None
        },
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    custom_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    artwork_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    unique_id_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'parent_id': {
            'data': 'TEXT',
            'sync': None
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
            'sync': None
        }
    }

    # TABLE, COLUMN
    table_index = (
        ('baseitem', 'id', ),
        ('movie', 'id', ),
        ('tvshow', 'id', ),
        ('season', 'id', ),
        ('episode', 'id', ),
        ('ratings', 'id', ),
        ('kodi_dbid', 'id', ),
        ('genre', 'id', ),
        ('country', 'id', ),
        ('studio', 'id', ),
        ('network', 'id', ),
        ('crew', 'id', ),
        ('cast', 'id', ),
        ('custom', 'id', ),
        ('artwork', 'id', ),
        ('unique_id', 'id', ),
    )

    @property
    def database_tables(self):
        return {
            'baseitem': self.baseitem_columns,
            'movie': self.movie_columns,
            'tvshow': self.tvshow_columns,
            'season': self.season_columns,
            'episode': self.episode_columns,
            'lactivities': self.lactivities_columns,
            'ratings': self.ratings_columns,
            'kodi_dbid': self.kodi_dbid_columns,
            'genre': self.genre_columns,
            'country': self.country_columns,
            'studio': self.studio_columns,
            'network': self.network_columns,
            'crew': self.crew_columns,
            'cast': self.cast_columns,
            'custom': self.custom_columns,
            'artwork': self.artwork_columns,
            'unique_id': self.unique_id_columns,
        }

    def create_database_execute(self, connection):
        for table, columns in self.database_tables.items():
            query = 'CREATE TABLE IF NOT EXISTS {}({})'
            query = query.format(table, ', '.join([f'{k} {v["data"]}' for k, v in columns.items()]))
            try:
                connection.execute(query)
            except Exception as error:
                self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        for table, column in self.table_index:
            query = 'CREATE INDEX {table}_{column}_x ON {table}({column})'.format(table=table, column=column)
            try:
                connection.execute(query)
            except Exception as error:
                self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)


class ItemDetailsDataBaseCache(DataBaseCache):
    cache_filename = 'ItemDetails.db'

    table = None  # Table in database
    conditions = ''  # WHERE conditions
    values = ()  # WHERE conditions values for ?
    keys = ()  # Keys to lookup
    online_data_func = None  # The function to get data e.g. get_response_json
    online_data_args = ()  # ARGS for online_data_func
    online_data_kwgs = {}  # KWGS for online_data_func
    data_cond = True  # Condition to retrieve any data

    @cached_property
    def cache(self):
        return ItemDetailsDataBase(filename=self.cache_filename)

    @cached_property
    def window(self):
        from jurialmunkey.window import WindowPropertySetter
        return WindowPropertySetter()

    @staticmethod
    def get_base_id(tmdb_type, tmdb_id):
        return f'{tmdb_type}.{tmdb_id}'

    @staticmethod
    def get_season_id(tmdb_type, tmdb_id, season):
        return f'{tmdb_type}.{tmdb_id}.{season}'

    @staticmethod
    def get_episode_id(tmdb_type, tmdb_id, season, episode):
        return f'{tmdb_type}.{tmdb_id}.{season}.{episode}'

    @property
    def online_data_cond(self):
        """ condition to determine whether to retrieve online data - defaults to data_cond """
        return self.data_cond

    @cached_property
    def online_data(self):
        """ cache online data from func to property """
        if not self.online_data_cond:
            return
        return self.online_data_func(*self.online_data_args, **self.online_data_kwgs)

    def get_online_data(self):
        """ function called when local cache does not have any data """
        return self.online_data

    @cached_property
    def data(self):
        if not self.data_cond:
            return
        return self.use_cached_many(
            self.conditions, self.values, self.keys, self.table,
            self.get_online_data
        )
