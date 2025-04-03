#!/usr/bin/python
# -*- coding: utf-8 -*-
from tmdbhelper.lib.addon.tmdate import set_timestamp
from tmdbhelper.lib.files.scache import SimpleCacheRowFactory


DEFAULT_TABLE = 'simplecache'


class DataBase(SimpleCacheRowFactory):

    simplecache_columns = {
        'data': {'data': 'TEXT', 'sync': None}
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

    def get_list_values(self, conditions, values, keys, table=DEFAULT_TABLE):
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
        query = 'SELECT {keys} FROM {table} WHERE id=? LIMIT 1'.format(
            keys=', '.join(keys),
            table=table)
        cache = self._execute_sql(query, (idx, ), read_only=True)
        if not cache:
            return
        return cache.fetchone()

    def set_values(self, idx, key_value_pairs, table=DEFAULT_TABLE):
        keys, values = zip(*key_value_pairs)
        query = 'UPDATE {table} SET {keys} WHERE id=?'.format(
            keys=', '.join([f'{k}=ifnull(?,{k})' for k in keys]),
            table=table)
        self.create_item(idx, table)
        return self._execute_sql(query, (*values, idx, ))

    def set_many_values(self, keys, data, table=DEFAULT_TABLE):
        """ {idx: key_value_pairs} """
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


class DataBaseCache:
    def get_cached(self, item_id, key, table):
        data = self.cache.get_values(item_id, keys=(key, ), table=table)
        return data[0] if data else None

    def set_cached(self, item_id, key, table, data):
        if not data:
            return
        key_value_pair = (key, data,)
        self.cache.set_values(item_id, key_value_pairs=(key_value_pair, ), table=table)
        return data

    def use_cached(self, item_id, key, table, func, *args, **kwargs):
        data = self.get_cached(item_id, key, table)
        if not data:
            data = self.set_cached(item_id, key, table, func(*args, **kwargs))
        return data

    def set_cached_many(self, keys, table, data):
        if not data:
            return
        self.cache.set_many_values(keys=keys, data=data, table=table)
        return data

    def use_cached_many(self, conditions, values, keys, table, func, *args, **kwargs):
        data = self.cache.get_list_values(conditions, values, keys, table)
        if not data:
            data = self.set_cached_many(keys, table, func(*args, **kwargs))
            data = self.cache.get_list_values(conditions, values, keys, table) if data else None
        return data
