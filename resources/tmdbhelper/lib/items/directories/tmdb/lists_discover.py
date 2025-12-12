# -*- coding: utf-8 -*-
from xbmcgui import Dialog, ListItem, INPUT_NUMERIC
from jurialmunkey.parser import try_int, merge_two_dicts, split_items
from tmdbhelper.lib.items.directories.tmdb.lists_standard import ListStandard, ListStandardProperties
from tmdbhelper.lib.items.container import ContainerDirectory
from tmdbhelper.lib.addon.plugin import ADDONPATH, PLUGINPATH, convert_type, get_localized, encode_url
from tmdbhelper.lib.addon.tmdate import get_datetime_now, get_timedelta
from jurialmunkey.window import get_property
from tmdbhelper.lib.query.database.database import FindQueriesDatabase
from tmdbhelper.lib.files.hcache import set_search_history, get_search_history
from tmdbhelper.lib.api.tmdb.api import TMDb
from jurialmunkey.ftools import cached_property
from urllib.parse import urlencode

from tmdbhelper.lib.addon.consts import (
    DISCOVER_REGIONS,
    DISCOVER_LANGUAGES,
    DISCOVER_RELEASE_TYPES,
    DISCOVER_SORTBY_MOVIES
)


RELATIVE_DATES = [
    'primary_release_date.gte', 'primary_release_date.lte', 'release_date.gte', 'release_date.lte',
    'air_date.gte', 'air_date.lte', 'first_air_date.gte', 'first_air_date.lte']


SORTBY_MOVIES = [i['id'] for i in DISCOVER_SORTBY_MOVIES]

SORTBY_TV = [
    'vote_average.desc', 'vote_average.asc', 'first_air_date.desc', 'first_air_date.asc',
    'popularity.desc', 'popularity.asc', 'vote_count.asc', 'vote_count.desc']


ALL_METHODS = [
    'open', 'with_separator', 'sort_by', 'add_rule', 'clear', 'save', 'with_cast', 'with_crew', 'with_people',
    'primary_release_year', 'primary_release_date.gte', 'primary_release_date.lte', 'release_date.gte', 'release_date.lte',
    'with_release_type', 'region', 'with_networks', 'air_date.gte', 'air_date.lte', 'first_air_date.gte',
    'first_air_date.lte', 'first_air_date_year', 'with_genres', 'without_genres', 'with_companies', 'with_keywords',
    'without_keywords', 'watch_region', 'with_watch_providers', 'with_original_language',
    'certification', 'certification.lte', 'certification.gte', 'certification_country',
    'vote_count.gte', 'vote_count.lte', 'vote_average.gte', 'vote_average.lte',
    'with_runtime.gte', 'with_runtime.lte', 'save_index', 'save_label']


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


def _get_release_types():
    return [
        {'id': i['id'], 'name': get_localized(i['name'])}
        for i in DISCOVER_RELEASE_TYPES
    ]


def _get_basedir_top(tmdb_type):
    return [
        {
            'label': get_localized(32174),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'open'}}]


def _get_basedir_new(tmdb_type):
    return [
        {
            'label': get_localized(32277),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'add_rule'}},
        {
            'label': get_localized(32239),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'with_separator'}},
        {
            'label': get_localized(32240),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'sort_by'}}]


def _get_basedir_end(tmdb_type):
    return [
        {
            'label': get_localized(192),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'clear'}},
        {
            'label': get_localized(190),
            'art': {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'},
            'params': {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': 'save'}}]


def _get_basedir_rules_movies():
    return [
        {'label': get_localized(32247), 'method': 'with_cast'},
        {'label': get_localized(32248), 'method': 'with_crew'},
        {'label': get_localized(32249), 'method': 'with_people'},
        {'label': get_localized(32250), 'method': 'primary_release_year'},
        {'label': get_localized(32251), 'method': 'primary_release_date.gte'},
        {'label': get_localized(32252), 'method': 'primary_release_date.lte'},
        {'label': get_localized(32253), 'method': 'release_date.gte'},
        {'label': get_localized(32254), 'method': 'release_date.lte'},
        {'label': get_localized(32255), 'method': 'with_release_type'},
        {'label': get_localized(32256), 'method': 'region'},
        {'label': get_localized(32486), 'method': 'certification'},
        {'label': get_localized(32488), 'method': 'certification.gte'},
        {'label': get_localized(32487), 'method': 'certification.lte'},
    ]


def _get_basedir_rules_tv():
    return [
        {'label': get_localized(32257), 'method': 'with_networks'},
        {'label': get_localized(32258), 'method': 'air_date.gte'},
        {'label': get_localized(32259), 'method': 'air_date.lte'},
        {'label': get_localized(32260), 'method': 'first_air_date.gte'},
        {'label': get_localized(32261), 'method': 'first_air_date.lte'},
        {'label': get_localized(32262), 'method': 'first_air_date_year'}]


def _get_basedir_rules(tmdb_type):
    items = [
        {'label': get_localized(32263), 'method': 'with_genres'},
        {'label': get_localized(32264), 'method': 'without_genres'},
        {'label': get_localized(32265), 'method': 'with_companies'},
        {'label': get_localized(32412), 'method': 'with_watch_providers'},
        {'label': get_localized(32268), 'method': 'with_keywords'},
        {'label': get_localized(32267), 'method': 'without_keywords'}]
    items += _get_basedir_rules_movies() if tmdb_type == 'movie' else _get_basedir_rules_tv()
    items += [
        {'label': get_localized(32269), 'method': 'with_original_language'},
        {'label': get_localized(32270), 'method': 'vote_count.gte'},
        {'label': get_localized(32271), 'method': 'vote_count.lte'},
        {'label': get_localized(32272), 'method': 'vote_average.gte'},
        {'label': get_localized(32273), 'method': 'vote_average.lte'},
        {'label': get_localized(32274), 'method': 'with_runtime.gte'},
        {'label': get_localized(32275), 'method': 'with_runtime.lte'}]
    return items


def _get_basedir_add(tmdb_type):
    basedir_items = []
    for i in _get_basedir_rules(tmdb_type):
        if not _win_prop(i.get('method')):
            continue
        i['params'] = {'info': 'user_discover', 'tmdb_type': tmdb_type, 'method': i.pop('method', None)}
        basedir_items.append(i)
    return basedir_items


def _get_formatted_item(item):
    try:
        affix = _win_prop(item['params']['method'], 'Label')
    except (KeyError, AttributeError):
        return item
    if affix:
        item['label'] = f'{item.get("label")}: {affix}'
    return item


def _get_discover_params(tmdb_type, get_labels=False):
    """ Set the params for the discover path based on user rules
    Takes an allowlist of rules to lookup window properties and place into params dict
    """
    params = {'info': 'discover', 'tmdb_type': tmdb_type, 'with_id': 'True'} if not get_labels else {}

    # Allowlist of rules to check for when building params
    rules = [{'method': 'with_separator'}, {'method': 'sort_by'}, {'method': 'watch_region'}, {'method': 'certification_country'}]
    rules += _get_basedir_rules(tmdb_type)

    # Check for window properties and add values to params
    prefix = 'Label' if get_labels else None
    for i in rules:
        method = i.pop('method', None)
        value = _win_prop(method, prefix)
        if not value:
            continue
        params[method] = value
    return params


def _win_prop(name, prefix=None, **kwargs):
    if not name:
        return
    prefix = f'UserDiscover.{prefix}' if prefix else 'UserDiscover'
    return get_property(f'{prefix}.{name}', **kwargs)


def _clear_properties(methods=ALL_METHODS):
    for method in methods:
        _win_prop(method, clear_property=True)
        _win_prop(method, 'Label', clear_property=True)


def _confirm_add(method):
    old_label = _win_prop(method, 'Label')
    old_value = _win_prop(method)
    if old_value or old_label:
        if Dialog().yesno(
                method, '\n'.join([get_localized(32099), old_label, get_localized(32100)]),
                yeslabel=get_localized(32101), nolabel=get_localized(32102)):
            return False
    return True


def _get_query(tmdb_type, method, query=None, header=None, use_details=False):
    item = FindQueriesDatabase().get_tmdb_id_from_query(
        tmdb_type=tmdb_type,
        query=query or Dialog().input(header),
        header=header or f'{get_localized(32276)} {tmdb_type}',
        use_details=use_details,
        get_listitem=True)
    if item and item.getUniqueID('tmdb'):
        return {'label': item.getLabel(), 'value': item.getUniqueID('tmdb'), 'method': method}


def _get_method(tmdb_type, method, header=None, use_details=False, confirmation=True):
    # If there's already values set then ask if the user wants to clear them instead of adding more
    if confirmation and not _confirm_add(method):
        return _clear_properties([method])

    # User inputs query, we look it up on TMDb and then ask them to select a choice
    properties = _get_query(tmdb_type, method, header=header, use_details=use_details)

    # Ask user if they want to try again if nothing selected or no results returned for query
    if not properties:
        if Dialog().yesno(
                get_localized(32103),
                get_localized(32104).format(tmdb_type)):
            return _get_method(tmdb_type, method, header, use_details, confirmation=False)
        return

    return properties


def _select_method(tmdb_type, header=None):
    rules = _get_basedir_rules(tmdb_type)
    x = Dialog().select(header, [i.get('label') for i in rules])
    if x != -1:
        return rules[x].get('method')


def _set_rule(method, label, value, overwrite=False):
    if not label or not value or not method:
        return
    old_value = None if overwrite else _win_prop(method)
    old_label = None if overwrite else _win_prop(method, 'Label')
    values = f'{old_value} / {value}' if old_value else f'{value}'
    labels = f'{old_label} / {label}' if old_label else f'{label}'
    _win_prop(method, set_property=values)
    _win_prop(method, 'Label', set_property=labels)


def _select_properties_dialog(data_list, header=None, multiselect=True):
    if not data_list:
        return
    func = Dialog().multiselect if multiselect else Dialog().select
    header = header or get_localized(32111)
    dialog_list = [i.get('name') for i in data_list]
    select_list = func(header, dialog_list)
    if (multiselect and not select_list) or (not multiselect and select_list == -1):
        return
    if not multiselect:
        select_list = [select_list]
    return select_list


def _select_properties(data_list, method, header=None, multiselect=True, separator=' / '):
    select_list = _select_properties_dialog(data_list, header, multiselect)
    if not select_list:
        return
    labels, values = None, None
    for i in select_list:
        label = data_list[i].get('name')
        value = data_list[i].get('id')
        if not value:
            continue
        labels = f'{labels} / {label}' if labels else label
        values = f'{values}{separator}{value}' if values else f'{value}'
    if labels and values:
        return {'label': labels, 'value': values, 'method': method}


def _get_genre(tmdb_type, method):
    data_list = FindQueriesDatabase().get_genres(tmdb_type)
    if not data_list:
        return
    data_list = [{'name': k, 'id': v} for k, v in data_list.items()]
    return _select_properties(data_list, method, header=get_localized(32112))


def _get_sorting(tmdb_type):
    sort_method_list = SORTBY_MOVIES if tmdb_type == 'movie' else SORTBY_TV
    sort_method = Dialog().select(get_localized(39010), sort_method_list)
    if sort_method != -1:
        return {'value': sort_method_list[sort_method], 'label': sort_method_list[sort_method], 'method': 'sort_by'}


def _get_separator():
    if Dialog().yesno(
            get_localized(32107), get_localized(32108),
            yeslabel=get_localized(32109), nolabel=get_localized(32110)):
        return {'value': 'OR', 'label': 'ANY', 'method': 'with_separator'}
    return {'value': 'AND', 'label': 'ALL', 'method': 'with_separator'}


def _get_numeric(method, header=None):
    value = Dialog().input(
        header, type=INPUT_NUMERIC, defaultt=_win_prop(method))
    return {'value': value, 'label': value, 'method': method}


def _get_keyboard(method, header=None):
    value = Dialog().input(
        header, defaultt=_win_prop(method))
    return {'value': value, 'label': value, 'method': method}


def _get_certification(method='certification'):
    # If there's already values set then ask if the user wants to clear them instead of adding more
    if not _confirm_add(method):
        return _clear_properties(['certification', 'certification.lte', 'certification.gte', 'certification_country'])

    # Don't ask for iso_country region again when adding more items
    iso_country = _win_prop('certification_country')

    tmdb = TMDb()
    query_database = FindQueriesDatabase()

    # Ask for iso country
    if not iso_country:
        all_certifications = query_database.get_certification('movie')
        all_certifications = [i['iso_country'] for i in all_certifications]

        try:
            preselect = all_certifications.index(tmdb.iso_country)
        except ValueError:
            preselect = -1

        x = Dialog().select(get_localized(20026), all_certifications, preselect=preselect)
        if x == -1:
            return
        iso_country = all_certifications[x]

    # Get certifications for region
    region_certifications = query_database.get_certification('movie', iso_country)
    gui_items = [i.get('certification') for i in region_certifications]

    x = Dialog().select(get_localized(32486), gui_items)
    if x == -1:
        return

    certification = region_certifications[x].get('certification')

    # Set region and return provider rule
    from urllib.parse import quote_plus
    _set_rule('certification_country', label=iso_country, value=iso_country, overwrite=True)
    return {
        'value': quote_plus(certification),
        'label': f"{certification} ({iso_country})",
        'method': method}


def _get_watch_provider(tmdb_type):
    # If there's already values set then ask if the user wants to clear them instead of adding more
    if not _confirm_add('with_watch_providers'):
        return _clear_properties(['with_watch_providers', 'watch_region'])

    # Don't ask for iso_country region again when adding more items
    iso_country = _win_prop('watch_region')
    iso_c_label = _win_prop('watch_region', 'Label')

    tmdb = TMDb()
    query_database = FindQueriesDatabase()

    # Get valid provider regions from TMDb
    if not iso_country:
        regions = query_database.provider_regions
        iso_regions = [k for k in regions.keys()]
        region_list = [f'{k} - {regions[k]}' for k in iso_regions]
        x = Dialog().select(
            get_localized(20026),
            region_list,
            preselect=iso_regions.index(tmdb.iso_country))
        if x == -1:
            return
        iso_country = iso_regions[x]
        iso_c_label = regions[iso_country]

    from tmdbhelper.lib.api.tmdb.images import TMDbImagePath
    tmdb_imagepath = TMDbImagePath()

    # Get providers for region

    providers = query_database.get_watch_providers(tmdb_type, iso_country)
    gui_items = []
    for i in providers:
        li = ListItem(i.get('provider_name'), f"{iso_c_label} ({iso_country}) - ID #{i.get('provider_id')}")
        li.setArt({'icon': tmdb_imagepath.get_imagepath_origin(i.get('logo_path'))})
        gui_items.append(li)
    x = Dialog().select(get_localized(19101), gui_items, useDetails=True)
    if x == -1:
        return
    provider = providers[x]

    # Set region and return provider rule
    _set_rule('watch_region', iso_country, iso_country, overwrite=True)
    return {
        'value': provider['provider_id'],
        'label': f"{provider['provider_name']} ({iso_country})",
        'method': 'with_watch_providers'}


def _edit_rules(idx=-1):
    """ Need to setup window properties if editing """
    if idx == -1:
        return
    history = get_search_history('discover')
    try:
        item = history[idx]
    except IndexError:
        return
    _clear_properties()  # Make sure old properties get cleared first
    _win_prop('save_index', set_property=f'{idx}')
    _win_prop('save_label', set_property=f'{item.get("label")}')
    for k, v in item.get('params', {}).items():
        if k in ['info', 'tmdb_type']:
            continue
        _win_prop(k, set_property=v)
        _win_prop(k, 'Label', set_property=item.get('labels', {}).get(k, v))


def _save_rules(tmdb_type):
    my_idx = try_int(_win_prop('save_index'), fallback=-1)
    params = _get_discover_params(tmdb_type)
    labels = _get_discover_params(tmdb_type, get_labels=True)
    label = _win_prop('save_label') if my_idx != -1 else Dialog().input(get_localized(32241))
    set_search_history(
        'discover',
        query={'label': label, 'params': params, 'labels': labels},
        replace=my_idx if my_idx != -1 else False)
    Dialog().ok(f'{get_localized(35259)} {label}', f'{params}')


def _add_rule(tmdb_type, method=None):
    if not method or method == 'add_rule':
        method = _select_method(tmdb_type, header=get_localized(32277))
    if not method:
        return
    rules = None
    overwrite = True
    if method == 'sort_by':
        rules = _get_sorting(tmdb_type)
    elif method == 'with_separator':
        rules = _get_separator()
    elif method in ['with_genres', 'without_genres']:
        rules = _get_genre(tmdb_type, method)
    elif method in ['with_cast', 'with_crew', 'with_people']:
        rules = _get_method('person', method, use_details=True)
        overwrite = False
    elif method == 'with_companies':
        rules = _get_method('company', method, use_details=False)
        overwrite = False
    elif method == 'with_watch_providers':
        rules = _get_watch_provider(tmdb_type)
        overwrite = False
    elif method in ['with_keywords', 'without_keywords']:
        rules = _get_method('keyword', method, use_details=False)
        overwrite = False
    elif method in ['certification', 'certification.lte', 'certification.gte']:
        rules = _get_certification(method)
    elif method == 'with_networks':
        rules = _get_keyboard(method, header=get_localized(32278))
    elif '_year' in method:
        rules = _get_numeric(method, header=get_localized(32279))
    elif 'vote_' in method or '_runtime' in method:
        rules = _get_numeric(method, header=get_localized(16028))
    elif '_date' in method:
        header = f'{get_localized(32114)} YYYY-MM-DD\n{get_localized(32113)}'
        rules = _get_keyboard(method, header=header)
    elif method == 'with_release_type':
        rules = _select_properties(_get_release_types(), method, header=get_localized(32119))
    elif method == 'region':
        rules = _select_properties(DISCOVER_REGIONS, method, header=get_localized(32120), multiselect=False)
    elif method == 'with_original_language':
        rules = _select_properties(DISCOVER_LANGUAGES, method, header=get_localized(32120), multiselect=True, separator='|')
    if not rules or not rules.get('value'):
        return
    _set_rule(method, rules.get('label'), rules.get('value'), overwrite=overwrite)


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


class ListDiscoverDir(ContainerDirectory):
    def get_items(self, **kwargs):
        def _get_discover_dir():
            items = []
            params = merge_two_dicts(kwargs, {'info': 'user_discover'})
            artwork = {'icon': f'{ADDONPATH}/resources/icons/themoviedb/default.png'}
            for i in ['movie', 'tv']:
                item = {
                    'label': f'{get_localized(32174)} {convert_type(i, "plural")}',
                    'params': merge_two_dicts(params, {'tmdb_type': i}),
                    'infoproperties': {'specialsort': 'top'},
                    'art': artwork}
                items.append(item)

            history_items = []
            history = get_search_history('discover')
            for x, i in enumerate(history):
                item_params = merge_two_dicts(kwargs, i.get('params', {}))
                edit_params = {'info': 'user_discover', 'tmdb_type': item_params.get('tmdb_type'), 'method': 'edit', 'idx': x}
                name_params = {'info': 'dir_discover', 'tmdb_type': item_params.get('tmdb_type'), 'method': 'rename', 'idx': x}
                dele_params = {'info': 'dir_discover', 'tmdb_type': item_params.get('tmdb_type'), 'method': 'delete', 'idx': x}
                item = {
                    'label': i.get('label'),
                    'params': item_params,
                    'art': artwork,
                    'context_menu': [
                        (get_localized(21435), f'Container.Update({encode_url(PLUGINPATH, **edit_params)})'),
                        (get_localized(118), f'Container.Update({encode_url(PLUGINPATH, **name_params)})'),
                        (get_localized(117), f'Container.Update({encode_url(PLUGINPATH, **dele_params)})')]}
                history_items.append(item)
            history_items.reverse()
            items += history_items

            if history:
                item = {
                    'label': get_localized(32237),
                    'art': artwork,
                    'params': merge_two_dicts(params, {'info': 'dir_discover', 'clear_cache': 'True'})}
                items.append(item)
            return items
        if kwargs.get('clear_cache') != 'True' and kwargs.get('method') not in ['delete', 'rename']:
            return _get_discover_dir()

        params = kwargs.copy()
        params.pop('clear_cache', None)
        params.pop('method', None)
        params.pop('idx', None)
        self.container_update = f'{encode_url(PLUGINPATH, **params)},replace'

        if kwargs.get('clear_cache') == 'True':
            set_search_history('discover', clear_cache=True)

        elif kwargs.get('method') == 'delete':
            idx = try_int(kwargs.get('idx', -1))
            if idx == -1:
                return
            set_search_history('discover', replace=idx)

        elif kwargs.get('method') == 'rename':
            idx = try_int(kwargs.get('idx', -1))
            if idx == -1:
                return
            history = get_search_history('discover')
            try:
                item = history[idx]
            except IndexError:
                return
            if not item:
                return
            item['label'] = Dialog().input('Rename', defaultt=item.get('label')) or item.get('label')
            set_search_history('discover', item, replace=idx)


class ListUserDiscover(ContainerDirectory):
    def get_items(self, tmdb_type, **kwargs):
        method = kwargs.get('method')

        # Method routing
        if not method or method == 'clear':
            _clear_properties()
        elif method == 'save':
            _save_rules(tmdb_type)
        elif method == 'edit':
            _edit_rules(idx=try_int(kwargs.get('idx'), fallback=-1))
        elif method == 'skip':
            pass
        else:
            _add_rule(tmdb_type, method)

        # Build directory items
        basedir_items = []
        basedir_items += _get_basedir_top(tmdb_type)
        basedir_items += _get_basedir_add(tmdb_type)
        basedir_items += _get_basedir_new(tmdb_type)
        if method != 'skip':
            basedir_items += _get_basedir_end(tmdb_type)

        self.update_listing = True if method and method != 'edit' else False
        self.container_content = 'files'

        items = [_get_formatted_item(i) for i in basedir_items]
        items[0]['params'] = _get_discover_params(tmdb_type)
        _win_prop('FolderPath', set_property=f"{PLUGINPATH}?{urlencode(items[0]['params'])}")
        _win_prop('ParamsDict', set_property=f"{items[0]['params']}")

        if method == 'skip':
            items.pop(0)

        return items
