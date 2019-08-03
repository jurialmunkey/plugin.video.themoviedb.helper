import requests
import utils
from globals import TMDB_API, _tmdb_apikey, _language


def make_request(request):
    request = requests.get(request)  # Request our data
    if not request.status_code == requests.codes.ok:  # Error Checking
        if request.status_code == 401:
            utils.invalid_apikey()
            exit()
        else:
            raise ValueError(request.raise_for_status())
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
    request = make_request(request)
    return request
