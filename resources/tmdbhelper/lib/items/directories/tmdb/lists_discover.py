# -*- coding: utf-8 -*-
from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int, split_items
from tmdbhelper.lib.addon.tmdate import get_datetime_now, get_timedelta
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties


RELATIVE_DATES = (
    'primary_release_date.gte',
    'primary_release_date.lte',
    'release_date.gte',
    'release_date.lte',
    'air_date.gte',
    'air_date.lte',
    'first_air_date.gte',
    'first_air_date.lte'
)


TRANSLATE_PARAMS = {
    'with_genres': ('genre', 'USER'),
    'without_genres': ('genre', 'USER'),
    'with_keywords': ('keyword', 'USER'),
    'without_keywords': ('keyword', 'USER'),
    'with_companies': ('company', 'NONE'),
    'with_watch_providers': (None, 'OR'),
    'with_people': ('person', 'USER'),
    'with_cast': ('person', 'USER'),
    'with_crew': ('person', 'USER'),
    'with_release_type': (None, 'OR'),
    'with_networks': (None, 'OR'),
}


class ListDiscoverProperties(ListStandardProperties):
    @cached_property
    def url(self):
        url = self.request_url.format(tmdb_type=self.tmdb_type)
        url = f'{url}{self.url_paramstring}'
        return url

    @cached_property
    def cache_name_tuple(self):
        cache_name_tuple = [f'{k}={v}' for k, v in self.translated_discover_params.items()]
        cache_name_tuple = sorted(cache_name_tuple)
        cache_name_tuple = [self.class_name, self.tmdb_type] + cache_name_tuple
        cache_name_tuple = cache_name_tuple + [self.page, self.pmax]
        return tuple(cache_name_tuple)

    discover_params_to_del = (
        'with_id', 'with_separator',
        'cacheonly', 'nextpage', 'widget', 'plugin_category', 'fanarttv',
        'tmdb_type', 'tmdb_id', 'page', 'limit', 'length', 'info')

    @cached_property
    def with_separator(self):
        return self.discover_params.get('with_separator')

    @cached_property
    def with_id(self):
        return bool(not self.discover_params.get('with_id'))

    @cached_property
    def tmdb_database(self):
        return self.tmdb_api.tmdb_database

    def get_url_separator(self, separator):
        return self.tmdb_api.get_url_separator(separator)

    def get_tmdb_id_list(self, items, tmdb_type=None, separator=None):
        """
        If tmdb_type specified will look-up IDs using search function otherwise assumes item ID is passed
        """
        separator = self.get_url_separator(separator)

        tmdb_id_list = (
            item
            if not tmdb_type else
            self.tmdb_database.genres.get(item)
            if tmdb_type == 'genre' else
            self.tmdb_database.get_tmdb_id(tmdb_type=tmdb_type, query=item)
            for item in items
        )
        tmdb_id_list = (i for i in tmdb_id_list if i)
        tmdb_id_list = separator.join(map(str, tuple(tmdb_id_list))) if separator else str(next(tmdb_id_list, ''))
        tmdb_id_list = tmdb_id_list or 'null'
        return tmdb_id_list

    def translate_key_value(self, key, value):
        if key not in TRANSLATE_PARAMS:
            return value
        items = split_items(value)
        ttype = TRANSLATE_PARAMS[key][0] if self.with_id else None
        stype = TRANSLATE_PARAMS[key][1] if TRANSLATE_PARAMS[key][1] != 'USER' else self.with_separator
        return self.get_tmdb_id_list(items, ttype, separator=stype)

    def relative_dates_key_value(self, key, value):
        datecode = value or ''
        datecode = datecode.lower()
        if datecode.startswith('t'):
            days = try_int(datecode[2:])
            days = -abs(days) if datecode[1:2] == '-' else days
            date = get_datetime_now() + get_timedelta(days=days)
            return date.strftime("%Y-%m-%d")
        return value

    def configure_key_value(self, key, value):
        if key in TRANSLATE_PARAMS:
            return self.translate_key_value(key, value)
        if key in RELATIVE_DATES:
            return self.relative_dates_key_value(key, value)
        return value

    @cached_property
    def translated_discover_params(self):
        # Convert to kwargs for use in URL encoded string
        translated_discover_params = {
            k: self.configure_key_value(k, v)
            for k, v in self.discover_params.items()
            if k not in self.discover_params_to_del
        }
        return translated_discover_params

    @cached_property
    def url_paramstring(self):
        if not self.translated_discover_params:
            return ''
        return f'?{"&".join([f"{k}={v}" for k, v in self.translated_discover_params.items()])}'


class ListDiscover(ListStandard):

    list_properties_class = ListDiscoverProperties

    def get_items(self, *args, **kwargs):
        self.list_properties.discover_params = kwargs
        return super().get_items(*args, **kwargs)

    def configure_list_properties(self, list_properties):
        list_properties = super().configure_list_properties(list_properties)
        list_properties.request_url = 'discover/{tmdb_type}'
        return list_properties
