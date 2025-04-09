#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.files.database import DataBaseCache, DataBase


class ItemDetailsDataBase(DataBase):

    baseitem_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
        },
        'mediatype': {
            'data': 'TEXT',
        },
        'expiry': {
            'data': 'INTEGER',
        },
    }

    movie_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
        },
        'mpaa': {
            'data': 'TEXT',
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
        'status': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
        },
        'trailer': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
        }
    }

    tvshow_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
        },
        'mpaa': {
            'data': 'TEXT',
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
        'status': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
        },
        'trailer': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
        }
    }

    season_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
        },
        'season': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
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
        },
        'tvshow_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'FOREIGN KEY(tvshow_id)': {
            'data': 'REFERENCES tvshow(id)',
        }
    }

    episode_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
        },
        'episode': {
            'data': 'INTEGER',
        },
        'year': {
            'data': 'INTEGER',
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
        },
        'duration': {
            'data': 'INTEGER',
        },
        'season_id': {
            'data': 'TEXT',
        },
        'tvshow_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'FOREIGN KEY(tvshow_id)': {
            'data': 'REFERENCES tvshow(id)',
        },
        'FOREIGN KEY(season_id)': {
            'data': 'REFERENCES season(id)',
        }
    }

    ratings_columns = {
        'id': {
            'data': 'TEXT UNIQUE',
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
        'rottentomatoes_reviewtotal': {
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
        'FOREIGN KEY(id)': {
            'data': 'REFERENCES baseitem(id)',
        }

    }

    person_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER UNIQUE',
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
    }

    genre_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
    }

    country_columns = {
        'name': {
            'data': 'TEXT',
        },
        'iso': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'UNIQUE': {
            'data': '(iso, parent_id)',
        }
    }

    studio_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'icon': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
    }

    network_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'icon': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
    }

    crewmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'role': {
            'data': 'TEXT',
        },
        'department': {
            'data': 'TEXT',
        },
        'ordering': {
            'data': 'INTEGER',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'FOREIGN KEY(tmdb_id)': {
            'data': 'REFERENCES person(tmdb_id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
    }

    castmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'role': {
            'data': 'TEXT',
        },
        'ordering': {
            'data': 'INTEGER',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'FOREIGN KEY(tmdb_id)': {
            'data': 'REFERENCES person(tmdb_id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
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
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        }
    }

    provider_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
        },
        'display_priority': {
            'data': 'INTEGER',
        },
        'iso': {
            'data': 'TEXT',
        },
        'logo': {
            'data': 'TEXT',
        },
        'availability': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        },
        'UNIQUE': {
            'data': '(tmdb_id, parent_id)',
        }
    }

    artwork_columns = {
        'key': {
            'data': 'TEXT',
        },
        'value': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
        }
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
        },
        'FOREIGN KEY(parent_id)': {
            'data': 'REFERENCES baseitem(id)',
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
        ('person', 'tmdb_id', ),
        ('genre', 'parent_id', ),
        ('studio', 'parent_id', ),
        ('network', 'parent_id', ),
        ('country', 'parent_id', ),
        ('castmember', 'parent_id', ),
        ('castmember', 'tmdb_id', ),
        ('crewmember', 'parent_id', ),
        ('crewmember', 'tmdb_id', ),
    )

    @property
    def database_tables(self):
        return {
            'baseitem': self.baseitem_columns,
            'movie': self.movie_columns,
            'tvshow': self.tvshow_columns,
            'season': self.season_columns,
            'episode': self.episode_columns,
            'ratings': self.ratings_columns,
            'person': self.person_columns,
            'genre': self.genre_columns,
            'country': self.country_columns,
            'studio': self.studio_columns,
            'network': self.network_columns,
            'crewmember': self.crewmember_columns,
            'castmember': self.castmember_columns,
            'provider': self.provider_columns,
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
