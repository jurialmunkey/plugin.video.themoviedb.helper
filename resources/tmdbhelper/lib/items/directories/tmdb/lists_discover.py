# -*- coding: utf-8 -*-
from jurialmunkey.parser import try_int, split_items
from tmdbhelper.lib.items.container import ContainerDefaultCacheDirectory
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.addon.tmdate import get_datetime_now, get_timedelta
from jurialmunkey.ftools import cached_property


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


class ListDiscoverDir(ContainerDefaultCacheDirectory):

    def get_winprop_params(self):
        from tmdbhelper.lib.script.discover.tmdb.main import WINPROP
        from jurialmunkey.parser import parse_paramstring
        from jurialmunkey.window import get_property

        try:
            paramstring = get_property(WINPROP)
            paramstring = paramstring.split('?')[1]
        except IndexError:
            return {}

        return parse_paramstring(paramstring)

    def get_static_item(self, label, params):
        from tmdbhelper.lib.addon.plugin import PLUGINPATH, ADDONPATH
        return {
            'label': label,
            'params': params,
            'path': PLUGINPATH,
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/discover.png'}
        }

    @property
    def item_new(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        params = self.get_winprop_params()
        params['info'] = 'user_discover'
        params['update_listing'] = 'true'
        return self.get_static_item(get_localized(21435), params)

    @property
    def item_browse(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        params = self.get_winprop_params()
        return self.get_static_item(get_localized(1024), params) if params else {}

    def get_items(self, **kwargs):
        from tmdbhelper.lib.script.discover.tmdb.main import NODE_FILENAME
        from tmdbhelper.lib.addon.consts import NODE_BASEDIR
        from tmdbhelper.lib.items.routes import get_container

        params = dict(
            filename=NODE_FILENAME,
            info='dir_custom_node',
            basedir=NODE_BASEDIR
        )

        paramstring = '&'.join((f'{k}={v}' for k, v in params.items()))
        container = get_container('dir_custom_node')(self.handle, paramstring, **params)

        items = []
        items.extend((i for i in (self.item_new, self.item_browse) if i))
        items.extend(container.get_directory(items_only=True, build_items=False) or [])

        return items


class ListUserDiscover(ListDiscoverDir):

    @property
    def update_listing(self):
        from jurialmunkey.parser import boolean
        return boolean(self.params.get('update_listing'))

    def get_items(self, update_listing=None, **kwargs):
        from tmdbhelper.lib.script.discover.tmdb.main import TMDbDiscover
        discover = TMDbDiscover()
        discover.load_values(**kwargs)
        discover.doModal()
        return super().get_items()
