import requests
import utils
import xbmc
import xbmcgui
import datetime
import simplecache
import time
import xml.etree.ElementTree as ET
from globals import TMDB_API, _tmdb_apikey, _language, OMDB_API, _omdb_apikey, OMDB_ARG, _addonname, _waittime, _cache_list_days, _cache_details_days, APPEND_TO_RESPONSE
_cache = simplecache.SimpleCache()


def invalid_apikey(api_name='TMDb'):
    xbmcgui.Dialog().ok('Missing/Invalid {0} API Key'.format(api_name),
                        'You must enter a valid {0} API key to use this add-on'.format(api_name))
    xbmc.executebuiltin('Addon.OpenSettings(plugin.video.themoviedb.helper)')


def my_rate_limiter(func):
    """
    Simple rate limiter
    """
    def decorated(*args, **kwargs):
        request = args[0]
        request_type = 'OMDb' if OMDB_API in request else 'TMDb'
        nart_time_id = '{0}{1}.nart_time_id'.format(_addonname, request_type)
        nart_lock_id = '{0}{1}.nart_lock_id'.format(_addonname, request_type)
        # Get our saved time value
        nart_time = xbmcgui.Window(10000).getProperty(nart_time_id)
        # If no value set to -1 to skip rate limiter
        nart_time = float(nart_time) if nart_time else -1
        nart_time = nart_time - time.time()
        # Apply rate limiting if next allowed request time is still in the furture
        if nart_time > 0:
            nart_lock = xbmcgui.Window(10000).getProperty(nart_lock_id)
            # If another instance is applying rate limiting then wait till it finishes
            while nart_lock == 'True':
                time.sleep(1)
                nart_lock = xbmcgui.Window(10000).getProperty(nart_lock_id)
            # Get the nart again because it might have elapsed
            nart_time = xbmcgui.Window(10000).getProperty(nart_time_id)
            nart_time = float(nart_time) if nart_time else -1
            nart_time = nart_time - time.time()
            # If nart still in the future then apply rate limiting
            if nart_time > 0:
                # Set the lock so another rate limiter cant run at same time
                xbmcgui.Window(10000).setProperty(nart_lock_id, 'True')
                while nart_time > 0:
                    time.sleep(1)
                    nart_time = nart_time - 1
        # Set nart into future for next request
        nart_time = time.time() + _waittime
        nart_time = str(nart_time)
        # Set the nart value
        xbmcgui.Window(10000).setProperty(nart_time_id, nart_time)
        # Unlock rate limiter so next instance can run
        xbmcgui.Window(10000).setProperty(nart_lock_id, 'False')
        # Run our function
        return func(*args, **kwargs)
    return decorated


def use_mycache(cache_days=_cache_details_days, suffix='', allow_api=True):
    def decorator(func):
        def decorated(*args, **kwargs):
            cache_name = _addonname
            if suffix:
                cache_name = u'{0}/{1}'.format(cache_name, suffix)
            for arg in args:
                if arg:
                    cache_name = u'{0}/{1}'.format(cache_name, arg)
            for key, value in kwargs.items():
                if value:
                    cache_name = u'{0}&{1}={2}'.format(cache_name, key, value)
            my_cache = _cache.get(cache_name)
            if my_cache:
                utils.kodi_log('CACHE REQUEST:\n{0}'.format(cache_name))
                return my_cache
            elif allow_api:
                utils.kodi_log('API REQUEST:\n{0}'.format(cache_name))
                my_objects = func(*args, **kwargs)
                if my_objects:
                    _cache.set(cache_name, my_objects, expiration=datetime.timedelta(days=cache_days))
                return my_objects
        return decorated
    return decorator


@my_rate_limiter
def make_request(request, is_json):
    request_type = 'OMDb' if OMDB_API in request else 'TMDb'
    utils.kodi_log('Requesting... {0}'.format(request), 1)
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            utils.kodi_log('HTTP Error Code: {0}'.format(request.status_code), 1)
            invalid_apikey(request_type)
            exit()
        else:
            utils.kodi_log('HTTP Error Code: {0}'.format(request.status_code), 1)
        return {}
    else:
        if is_json:
            request = request.json()  # Make the request nice
        return request


@use_mycache(_cache_list_days, 'tmdb_api')
def tmdb_api_request(*args, **kwargs):
    """
    Request from TMDb API and store in cache for 24 hours
    Use when requesting lists that change regular (e.g. Popular / Airing etc.)
    """
    request = TMDB_API
    for arg in args:
        if arg:  # Don't add empty args
            request = '{0}/{1}'.format(request, arg)
    request = '{0}{1}{2}'.format(request, _tmdb_apikey, _language)
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = '{0}&{1}={2}'.format(request, key, value)
    request = make_request(request, True)
    return request


@use_mycache(_cache_details_days, 'tmdb_api')
def tmdb_api_request_longcache(*args, **kwargs):
    """
    Request from TMDb API and store in cache for 14 days
    Use when requesting movie details or other info that doesn't change regularly
    """
    return tmdb_api_request(*args, **kwargs)


@use_mycache(_cache_details_days, 'tmdb_api', False)
def tmdb_api_only_cached(*args, **kwargs):
    """
    Check if look-up available in cache a return that. Otherwise return nothing
    """
    return None


@use_mycache(_cache_details_days, 'omdb_api')
def omdb_api_request(*args, **kwargs):
    """ Request from OMDb API and store in cache for 14 days"""
    request = OMDB_API
    request = '{0}{1}{2}&r=xml'.format(request, _omdb_apikey, OMDB_ARG)
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = '{0}&{1}={2}'.format(request, key, value)
    request = make_request(request, False)
    if request:
        request = ET.fromstring(request.content)
        request = utils.dictify(request)
    if request and request.get('root') and not request.get('root').get('response') == 'False':
        request = request.get('root').get('movie')[0]
    else:
        request = {}
    return request


@use_mycache(_cache_details_days, 'omdb_api', False)
def omdb_api_only_cached(*args, **kwargs):
    """
    Check if look-up available in cache a return that. Otherwise return nothing
    """
    return None


def get_cached_data(item=None, tmdb_type=None):
    detailed_item = None
    if tmdb_type and item:
        if item.get('show_id') or item.get('id'):
            if item.get('show_id'):
                my_id = item.get('show_id')
                my_request = 'tv'
            elif item.get('id'):
                my_id = item.get('id')
                my_request = tmdb_type
            if my_request in ['movie', 'tv']:
                request_path = '{0}/{1}'.format(my_request, my_id)
                kwparams = {}
                kwparams['append_to_response'] = APPEND_TO_RESPONSE
                detailed_item = tmdb_api_only_cached(request_path, **kwparams)
    if detailed_item:
        detailed_item = utils.merge_two_dicts(detailed_item, item)
        return detailed_item
    else:
        return item


def translate_lookup_ids(items, request, lookup_dict=False, separator='%2C'):
    if items:
        items = utils.split_items(items)
        temp_list = ''
        for item in items:
            query = None
            item_id = None
            if request:  # If we don't have TMDb IDs then look them up
                if lookup_dict:  # Check if we should be looking up in a stored dict
                    if request.get(item):
                        item_id = str(request.get(item))
                else:  # Otherwise lookup IDs via a TMDb search request
                    query = tmdb_api_request_longcache(request, query=item)
                    if query:
                        if query.get('results') and query.get('results')[0]:
                            item_id = query.get('results')[0].get('id')
            else:  # Otherwise we assume that each item is a TMDb ID
                item_id = item
            if item_id:
                if separator:  # If we've got a url separator then concatinate the list with it
                    temp_list = '{0}{1}{2}'.format(temp_list, separator, item_id) if temp_list else item_id
                else:  # If no separator, assume that we just want to use the first found ID
                    temp_list = str(item_id)
                    break  # Stop once we have a item
        temp_list = temp_list if temp_list else 'null'
        return temp_list
