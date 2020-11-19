import simplecache
from resources.lib.addon.plugin import kodi_log, format_name
from resources.lib.files.utils import get_pickle_name
from resources.lib.addon.timedate import get_timedelta
_cache = simplecache.SimpleCache()
_cache_name = 'TMDbHelper_v4.0.2'
CACHE_LONG = 14
CACHE_SHORT = 1
CACHE_EXTENDED = 90


def use_simple_cache(cache_days=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs['cache_days'] = cache_days or kwargs.get('cache_days', None)
            kwargs['cache_combine_name'] = True
            kwargs['cache_name'] = '{}.'.format(func.__name__)
            kwargs['cache_name'] = '{}.{}'.format(args[0].__class__.__name__, kwargs['cache_name'])
            return use_cache(func, *args, **kwargs)
        return wrapper
    return decorator


def get_cache(cache_name):
    cache_name = get_pickle_name(cache_name or '')
    return _cache.get('{}.{}'.format(_cache_name, cache_name))


def set_cache(my_object, cache_name, cache_days=14, force=False, fallback=None):
    cache_name = get_pickle_name(cache_name or '')
    if my_object and cache_name and cache_days:
        _cache.set('{}.{}'.format(_cache_name, cache_name), my_object, expiration=get_timedelta(days=cache_days))
    elif force:
        my_object = my_object or fallback
        cache_days = force if isinstance(force, int) else cache_days
        _cache.set('{}.{}'.format(_cache_name, cache_name), my_object, expiration=get_timedelta(days=cache_days))
    return my_object


def use_cache(func, *args, **kwargs):
    """
    Simplecache takes func with args and kwargs
    Returns the cached item if it exists otherwise does the function
    """
    cache_days = kwargs.pop('cache_days', 14) or 14
    cache_name = kwargs.pop('cache_name', '') or ''
    cache_only = kwargs.pop('cache_only', False) or False
    cache_force = kwargs.pop('cache_force', False) or False
    cache_fallback = kwargs.pop('cache_fallback', False) or False
    cache_refresh = kwargs.pop('cache_refresh', False) or False
    cache_combine_name = kwargs.pop('cache_combine_name', False) or False
    headers = kwargs.pop('headers', None) or None
    if not cache_name or cache_combine_name:
        cache_name = format_name(cache_name, *args, **kwargs)
    my_cache = get_cache(cache_name) if not cache_refresh else None
    if my_cache:
        return my_cache
    if not cache_only:
        if headers:
            kwargs['headers'] = headers
        my_object = func(*args, **kwargs)
        return set_cache(my_object, cache_name, cache_days, force=cache_force, fallback=cache_fallback)


def get_search_history(tmdb_type=None):
    if not tmdb_type:
        return []
    cache_name = 'search.history.{}'.format(tmdb_type)
    return get_cache(cache_name) or []


def _add_search_history(tmdb_type=None, query=None, max_entries=9, **kwargs):
    search_history = get_search_history(tmdb_type)
    if query in search_history:  # Remove query if in history because we want it to be first in list
        search_history.remove(query)
    if max_entries and len(search_history) > max_entries:
        search_history.pop(0)  # Remove the oldest query if we hit our max so we don't accumulate months worth of queries
    if query:
        search_history.append(query)
    return search_history


def _replace_search_history(tmdb_type=None, query=None, replace=None, **kwargs):
    search_history = get_search_history(tmdb_type)
    if not isinstance(replace, int) and replace in search_history:
        replace = search_history.index(replace)  # If not an int then we need to look-up index of the item to replace
    if not isinstance(replace, int):
        return  # If we can't find an index don't update the cache so we don't cause unintended modification
    try:  # Use a try block to catch index out of range errors or other issues with updating history
        if query:
            search_history[replace] = query
        else:
            search_history.pop(replace)
    except Exception as exc:
        kodi_log(exc, 1)
        return
    kodi_log(search_history, 1)
    return search_history


def set_search_history(tmdb_type=None, query=None, cache_days=120, clear_cache=False, max_entries=9, replace=False):
    if not tmdb_type:
        return
    cache_name = 'search.history.{}'.format(tmdb_type)
    if not clear_cache:
        func = _add_search_history if replace is False else _replace_search_history
        search_history = func(tmdb_type=tmdb_type, query=query, max_entries=max_entries, replace=replace)
        set_cache(search_history, cache_name=cache_name, cache_days=cache_days, force=True)
    return set_cache(None, cache_name, 0, force=True) if clear_cache else query
