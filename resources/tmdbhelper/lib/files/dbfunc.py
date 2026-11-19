#!/usr/bin/python
# -*- coding: utf-8 -*-


class DatabaseAccess:
    """Read and write cached values of self.cache in the current thread's session."""

    # ======================================
    # Single item with single key/value pair
    # ======================================

    def del_cached(self, table, item_id, children=True):
        self.cache.del_item(table, item_id)
        if not children:
            return
        self.cache.del_item_like(table, f'{item_id}.%')

    def get_cached(self, table, item_id, key):
        data = self.cache.get_values(table, item_id, keys=(key, ))
        return data[0] if data else None

    def set_cached(self, table, item_id, key, value):
        """ Set key to value for id=item_id in table """
        self.cache.set_item_values(table, item_id, keys=(key, ), values=(value, ))

    def use_cached(self, table, item_id, key, func, *args, **kwargs):
        """ Get key for id=item_id in table else set key to func(*args, **kwargs) """
        internal_data = self.get_cached(table, item_id, key)

        def get_external_data():
            external_data = func(*args, **kwargs)
            if not external_data:
                return
            self.set_cached(table, item_id, key, external_data)
            return self.get_cached(table, item_id, key)

        return internal_data or get_external_data()

    # =========================================
    # Single item with multiple key/value pairs
    # =========================================

    def get_cached_values(self, table, item_id, keys):
        return self.cache.get_values(table, item_id, keys)

    def set_cached_values(self, table, item_id, keys, values):
        self.cache.set_item_values(table, item_id, keys, values)

    # ============================================
    # Multiple items with multiple key/value pairs
    # ============================================

    def get_cached_list_values(self, table, keys, values, conditions):
        return self.cache.get_list_values(table, keys, values, conditions)

    def set_cached_list_values(self, table, keys, values, overwrite=False):
        self.cache.set_list_values(table, keys, values, overwrite=overwrite)

    def set_or_update_null_cached_list_values(self, table, keys, values, conflict_constraint='id'):
        self.cache.set_or_update_null_list_values(table, keys, values, conflict_constraint=conflict_constraint)

    def set_cached_many(self, table, keys, data):
        self.cache.set_many_values(table, keys, data)

    def use_cached_many(self, table, keys, values, conditions, func, *args, **kwargs):
        internal_data = self.get_cached_list_values(table, keys, values, conditions)

        def get_external_data():
            external_data = func(*args, **kwargs)
            if not external_data:
                return
            self.set_cached_many(table, keys, external_data)
            return self.get_cached_list_values(table, keys, values, conditions)

        return internal_data or get_external_data()
