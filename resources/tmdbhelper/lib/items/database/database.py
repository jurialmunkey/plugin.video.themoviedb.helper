#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.files.database import DataBase


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
        'duration': {
            'data': 'INTEGER',
        },
        'tagline': {
            'data': 'TEXT',
        },
        'premiered': {
            'data': 'TEXT',
        },
        'status': {
            'data': 'TEXT',
        },
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
        },
        'status': {
            'data': 'TEXT',
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
        'status': {
            'data': 'TEXT',
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
        'status': {
            'data': 'TEXT',
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

    ratings_columns = {
        'parent_id': {
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
            'foreign_key': 'company(tmdb_id)',
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

    crewmember_columns = {
        'tmdb_id': {
            'data': 'INTEGER',
            'foreign_key': 'person(tmdb_id)',
            'indexed': True,
            'unique': True
        },
        'role': {
            'data': 'TEXT',
        },
        'department': {
            'data': 'TEXT',
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
            'foreign_key': 'person(tmdb_id)',
            'indexed': True,
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
        },
        'name': {
            'data': 'TEXT',
        },
        'iso_country': {
            'data': 'TEXT',
        },
        'logo': {
            'data': 'TEXT',
        },
    }

    art_columns = {
        'aspect_ratio': {
            'data': 'TEXT',
            'indexed': True
        },
        'height': {
            'data': 'INTEGER',
        },
        'width': {
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
            'indexed': True
        },
        'extension': {
            'data': 'TEXT',
            'indexed': True
        },
        'vote_average': {
            'data': 'INTEGER',
            'indexed': True
        },
        'vote_count': {
            'data': 'INTEGER',
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
            'company': self.company_columns,
            'video': self.video_columns,
            'certification': self.certification_columns,
            'crewmember': self.crewmember_columns,
            'castmember': self.castmember_columns,
            'provider': self.provider_columns,
            'service': self.service_columns,
            'custom': self.custom_columns,
            'art': self.art_columns,
            'unique_id': self.unique_id_columns,
        }

    def create_database_execute(self, connection):

        def create_column_data(columns):
            return [f'{k} {v["data"]}' for k, v in columns.items()]

        def create_column_fkey(columns):
            return [f'FOREIGN KEY({k}) REFERENCES {v["foreign_key"]} ON DELETE CASCADE' for k, v in columns.items() if 'foreign_key' in v]

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
