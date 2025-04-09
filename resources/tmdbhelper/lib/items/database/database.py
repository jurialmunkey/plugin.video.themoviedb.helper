#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import cached_property
from tmdbhelper.lib.files.database import DataBaseCache, DataBase


class ItemDetailsDataBase(DataBase):

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
        },
    }

    movie_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
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
        }
    }

    tvshow_columns = {
        'id': {
            'data': 'TEXT PRIMARY KEY',
            'foreign_key': 'baseitem(id)',
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
        }
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
            'foreign_key': 'tvshow(id)',
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
            'foreign_key': 'season(id)',
        },
        'tvshow_id': {
            'data': 'TEXT',
            'foreign_key': 'tvshow(id)',
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
    }

    person_columns = {
        'tmdb_id': {
            'data': 'INTEGER PRIMARY KEY',
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
            'unique': True
        },
    }

    country_columns = {
        'name': {
            'data': 'TEXT',
        },
        'iso': {
            'data': 'TEXT',
            'unique': True
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'unique': True
        },
    }

    studio_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True
        },
        'icon': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'unique': True
        },
    }

    network_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True
        },
        'icon': {
            'data': 'TEXT',
        },
        'country': {
            'data': 'TEXT',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
            'unique': True
        },
    }

    crewmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'foreign_key': 'person(tmdb_id)',
            'unique': True
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
            'foreign_key': 'baseitem(id)',
            'unique': True
        },
    }

    castmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'foreign_key': 'person(tmdb_id)',
            'unique': True
        },
        'role': {
            'data': 'TEXT',
        },
        'ordering': {
            'data': 'INTEGER',
        },
        'parent_id': {
            'data': 'TEXT',
            'foreign_key': 'baseitem(id)',
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
        },
    }

    provider_columns = {
        'name': {
            'data': 'TEXT',
        },
        'tmdb_id': {
            'data': 'INTEGER',
            'unique': True
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
            'foreign_key': 'baseitem(id)',
            'unique': True
        },
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
            'foreign_key': 'baseitem(id)',
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
        },
    }

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

        def create_column_data(columns):
            return [f'{k} {v["data"]}' for k, v in columns.items()]

        def create_column_fkey(columns):
            return [f'FOREIGN KEY({k}) REFERENCES {v["foreign_key"]}' for k, v in columns.items() if 'foreign_key' in v]

        def create_column_uids(columns):
            keys = [k for k, v in columns.items() if v.get('unique')]
            if not keys:
                return []
            return ['UNIQUE ({})'.format(', '.join(keys))]

        for table, columns in self.database_tables.items():
            query = []
            query += create_column_data(columns)
            query += create_column_fkey(columns)
            query += create_column_uids(columns)
            query = 'CREATE TABLE IF NOT EXISTS {table}({query})'.format(table=table, query=', '.join(query))
            try:
                connection.execute(query)
            except Exception as error:
                self.kodi_log(f'CACHE: Exception while initializing _database: {error}\n{self._sc_name} - {query}', 1)

        for table, columns in self.database_tables.items():
            for column, v in columns.items():
                if not v.get('indexed'):
                    continue
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
