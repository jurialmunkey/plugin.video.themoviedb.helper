import requests
import utils
from utils import kodi_log
import xbmc
import xbmcgui
import datetime
import simplecache
import time
import xml.etree.ElementTree as ET
from globals import TMDB_API, _tmdb_apikey, _language, OMDB_API, _omdb_apikey, OMDB_ARG, _addonname, _waittime, _cache_list_days, _cache_details_days
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
        nart_time_id = '{0}nart_time_id'.format(_addonname)
        nart_lock_id = '{0}nart_lock_id'.format(_addonname)
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
                cache_name = '{0}/{1}'.format(cache_name, suffix)
            for arg in args:
                if arg:
                    cache_name = '{0}/{1}'.format(cache_name, arg)
            for key, value in kwargs.items():
                if value:
                    cache_name = '{0}&{1}={2}'.format(cache_name, key, value)
            my_cache = _cache.get(cache_name)
            if my_cache:
                kodi_log('CACHE REQUEST:\n{0}'.format(cache_name))
                return my_cache
            elif allow_api:
                kodi_log('API REQUEST:\n{0}'.format(cache_name))
                my_objects = func(*args, **kwargs)
                _cache.set(cache_name, my_objects, expiration=datetime.timedelta(days=cache_days))
                return my_objects
        return decorated
    return decorator


@my_rate_limiter
def make_request(request, is_json):
    request_type = 'OMDb' if OMDB_API in request else 'TMDb'
    kodi_log('Requesting... {0}'.format(request), 1)
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            kodi_log('HTTP Error Code: {0}'.format(request.status_code), 1)
            invalid_apikey(request_type)
            exit()
        else:
            kodi_log('HTTP Error Code: {0}'.format(request.status_code), 1)
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
