import re
import sys
try:
    from urllib.parse import urlencode, unquote_plus  # Py3
except ImportError:
    from urllib import urlencode, unquote_plus


PLUGINPATH = u'plugin://plugin.video.themoviedb.helper/'


def try_int(string, base=None, fallback=0):
    '''helper to parse int from string without erroring on empty or misformed string'''
    try:
        return int(string, base) if base else int(string)
    except Exception:
        return fallback


def try_float(string):
    '''helper to parse float from string without erroring on empty or misformed string'''
    try:
        return float(string or 0)
    except Exception:
        return 0


def try_str(value):
    '''helper to stringify value'''
    try:
        return u'{}'.format(value)
    except Exception:
        return ''


def try_type(value, output=None):
    if output == int:
        return try_int(value)
    if output == str:
        return try_str(value)
    if output == float:
        return try_float(value)


def try_decode(string, encoding='utf-8', errors=None):
    """helper to decode strings for PY 2 """
    if sys.version_info.major == 3:
        return string
    try:
        return string.decode(encoding, errors) if errors else string.decode(encoding)
    except Exception:
        return string


def try_encode(string, encoding='utf-8'):
    """helper to encode strings for PY 2 """
    if sys.version_info.major == 3:
        return string
    try:
        return string.encode(encoding)
    except Exception:
        return string


def parse_paramstring(paramstring):
    """ helper to assist with difference in urllib modules in PY2/3 """
    params = dict()
    paramstring = paramstring.replace('&amp;', '&')  # Just in case xml string
    for param in paramstring.split('&'):
        if '=' not in param:
            continue
        k, v = param.split('=')
        params[unquote_plus(k)] = unquote_plus(v)
    return params


def urlencode_params(*args, **kwargs):
    """ helper to assist with difference in urllib modules in PY2/3 """
    params = dict()
    for k, v in kwargs.items():  # TODO: Switch to viewitems and remove viewitems from plugin and put in this module
        params[try_encode(k)] = try_encode(v)
    return urlencode(params)


def encode_url(path=None, **kwargs):
    path = path or PLUGINPATH
    paramstring = u'?{}'.format(urlencode_params(**kwargs)) if kwargs else ''
    return u'{}{}'.format(path, paramstring)


def get_between_strings(string, startswith='', endswith=''):
    exp = startswith + '(.+?)' + endswith
    try:
        return re.search(exp, string).group(1)
    except AttributeError:
        return ''
