import requests
import utils
import xbmc
import datetime
import simplecache
import time
import xml.etree.ElementTree as ET
from globals import TMDB_API, _tmdb_apikey, _language, OMDB_API, _omdb_apikey, OMDB_ARG, _addonlogname, _addonname
_cache = simplecache.SimpleCache()
_waittime = 1


def cache_last_used_time(func):
    """
    Simple rate limiter
    """
    def decorated(*args, **kwargs):
        cache_name = _addonname + '.last_used_time'
        cached_time = _cache.get(cache_name)
        current_time = time.time()
        time_diff = cached_time - current_time if cached_time else -1
        if time_diff < 0:
            cached_time = current_time + _waittime
            _cache.set(cache_name, cached_time, expiration=datetime.timedelta(days=14))
            return func(*args, **kwargs)
        else:
            xbmc.log(_addonlogname + 'Rate Limiter Waiting ' + str(time_diff) + ' Seconds...', level=xbmc.LOGNOTICE)
            time.sleep(time_diff)
            return func(*args, **kwargs)
    return decorated


def use_mycache(cache_days=14, suffix=''):
    def decorator(func):
        def decorated(*args, **kwargs):
            cache_name = _addonname
            if suffix:
                cache_name = cache_name + '/' + suffix
            for arg in args:
                if arg:
                    cache_name = cache_name + '/' + arg
            for key, value in kwargs.items():
                if value:
                    cache_name = cache_name + '&' + key + '=' + value
            my_cache = _cache.get(cache_name)
            if my_cache:
                xbmc.log(_addonlogname + 'CACHE REQUEST:\n' + cache_name, level=xbmc.LOGNOTICE)
                return my_cache
            else:
                xbmc.log(_addonlogname + 'API REQUEST:\n' + cache_name, level=xbmc.LOGNOTICE)
                my_objects = func(*args, **kwargs)
                _cache.set(cache_name, my_objects, expiration=datetime.timedelta(days=cache_days))
                return my_objects
        return decorated
    return decorator


def make_request(request, is_json):
    xbmc.log(_addonlogname + 'Requesting... ' + request, level=xbmc.LOGNOTICE)
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            xbmc.log(_addonlogname + 'HTTP Error Code: ' + str(request.status_code), level=xbmc.LOGNOTICE)
            utils.invalid_apikey()
            exit()
        else:
            xbmc.log(_addonlogname + 'HTTP Error Code: ' + str(request.status_code), level=xbmc.LOGNOTICE)
    if is_json:
        request = request.json()  # Make the request nice
    return request


@use_mycache(1, 'tmdb_api')
def tmdb_api_request(*args, **kwargs):
    """
    Request from TMDb API and store in cache for 24 hours
    Use when requesting lists that change regular (e.g. Popular / Airing etc.)
    """
    request = TMDB_API
    for arg in args:
        if arg:  # Don't add empty args
            request = request + '/' + arg
    request = request + _tmdb_apikey + _language
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = request + '&' + key + '=' + value
    request = make_request(request, True)
    return request


@use_mycache(14, 'tmdb_api')
def tmdb_api_request_longcache(*args, **kwargs):
    """
    Request from TMDb API and store in cache for 14 days
    Use when requesting movie details or other info that doesn't change regularly
    """
    return tmdb_api_request(*args, **kwargs)


@use_mycache(14, 'omdb_api')
def omdb_api_request(*args, **kwargs):
    """ Request from OMDb API and store in cache for 14 days"""
    request = OMDB_API
    request = request + _omdb_apikey + OMDB_ARG + '&r=xml'
    for key, value in kwargs.items():
        if value:  # Don't add empty kwargs
            request = request + '&' + key + '=' + value
    request = make_request(request, False)
    request = ET.fromstring(request.content)
    request = utils.dictify(request)
    if request and request.get('root') and not request.get('root').get('response') == 'False':
        request = request.get('root').get('movie')[0]
    else:
        request = {}
    return request
