#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.files.scache import SimpleCache


DEFAULT_TABLE = 'simplecache'


class SyncDataBase(SimpleCache):

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
        'slug': {
            'data': 'TEXT',
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
    lactivities_columns = {
        'data': {'data': 'TEXT', 'sync': None}
    }

    def _do_cleanup(self, *args, **kwargs):
        cur_time = set_timestamp(0, True)
        self.set_window_property(f'{self._sc_name}.clean.lastexecuted', str(cur_time))

    def set_activity(self, item_type, method, value):
        idx = f'{item_type}.{method}'
        query = 'INSERT OR REPLACE INTO lactivities( id, data) VALUES (?, ?)'
        return self._execute_sql(query, (idx, value, ))

    def get_activity(self, item_type, method):
        idx = f'{item_type}.{method}'
        query = 'SELECT data FROM lactivities WHERE id=? LIMIT 1'
        cache = self._execute_sql(query, (idx, ))
        if not cache:
            return
        cache = cache.fetchone()
        if not cache:
            return
        return cache[0]

    def keys_are_valid(self, keys, table):
        columns_keys = getattr(self, f'{table}_columns')
        for k in keys:
            if k not in columns_keys.keys():
                return False
        return True

    def get_list_values(self, conditions, values, keys, table=DEFAULT_TABLE):
        if not self.keys_are_valid(keys, table):
            return
        query = 'SELECT {keys} FROM {table} WHERE {conditions}'.format(
            keys=', '.join(keys),
            table=table,
            conditions=conditions,
        )
        cache = self._execute_sql(query, values, read_only=True)
        if not cache:
            return
        return cache.fetchall()

    def get_values(self, idx, keys, table=DEFAULT_TABLE):
        if not self.keys_are_valid(keys, table):
            return
        query = 'SELECT {keys} FROM {table} WHERE id=? LIMIT 1'.format(
            keys=', '.join(keys),
            table=table)
        cache = self._execute_sql(query, (idx, ), read_only=True)
        if not cache:
            return
        return cache.fetchone()

    def set_values(self, idx, key_value_pairs, table=DEFAULT_TABLE):
        keys, values = zip(*key_value_pairs)
        if not self.keys_are_valid(keys, table):
            return
        query = 'UPDATE {table} SET {keys} WHERE id=?'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]),
            table=table)
        self.create_item(idx, table)
        return self._execute_sql(query, (*values, idx, ))

    def set_many_values(self, keys, data, table=DEFAULT_TABLE):
        """ {idx: key_value_pairs} """
        if not self.keys_are_valid(keys, table):
            return
        query = 'UPDATE {table} SET {keys} WHERE id=?'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]),
            table=table)
        self.create_many_items([idx for idx in data.keys()], table)
        return self._execute_sql(query, [(*values, idx, ) for idx, values in data.items()])

    def del_column_values(self, keys, item_type, table=DEFAULT_TABLE):
        query = 'UPDATE {table} SET {keys} WHERE item_type=?'.format(
            keys=', '.join([f'{k}=NULL' for k in keys]),
            table=table)
        return self._execute_sql(query, (item_type, ))

    def create_item(self, idx, table=DEFAULT_TABLE):
        query = 'INSERT OR IGNORE INTO {table}( id) VALUES (?)'.format(table=table)
        self._execute_sql(query, (idx,))

    def create_many_items(self, items, table=DEFAULT_TABLE):
        query = 'INSERT OR IGNORE INTO {table}( id) VALUES (?)'.format(table=table)
        self._execute_sql(query, [(idx,) for idx in items])

    @property
    def database_tables(self):
        return {
            'simplecache': self.simplecache_columns,
            'lactivities': self.lactivities_columns,
        }

    def create_database_execute(self, connection):
        for table, columns in self.database_tables.items():
            query = 'CREATE TABLE IF NOT EXISTS {}(id TEXT UNIQUE, {})'
            query = query.format(table, ', '.join([f'{k} {v["data"]}' for k, v in columns.items()]))
            connection.execute(query)
