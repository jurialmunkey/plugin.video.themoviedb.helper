import requests
import utils
import xbmc
import xml.etree.ElementTree as ET
from globals import TMDB_API, _tmdb_apikey, _language, OMDB_API, _omdb_apikey, OMDB_ARG, _addonname


def make_request(request, is_json):
    xbmc.log(_addonname + 'Requesting... ' + request, level=xbmc.LOGNOTICE)
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            xbmc.log(_addonname + 'HTTP Error Code: ' + str(request.status_code), level=xbmc.LOGNOTICE)
            utils.invalid_apikey()
            exit()
        else:
            xbmc.log(_addonname + 'HTTP Error Code: ' + str(request.status_code), level=xbmc.LOGNOTICE)
    if is_json:
        request = request.json()  # Make the request nice
    return request


def tmdb_api_request(*args, **kwargs):
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


def omdb_api_request(**kwargs):
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
