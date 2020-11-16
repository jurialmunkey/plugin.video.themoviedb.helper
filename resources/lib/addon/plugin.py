#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import xbmc
import xbmcaddon
import hashlib
from resources.lib.addon.constants import LANGUAGES
from resources.lib.addon.parser import try_decode
if sys.version_info[0] >= 3:
    unicode = str  # In Py3 str is now unicode


ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')
ADDONPATH = ADDON.getAddonInfo('path')
PLUGINPATH = u'plugin://plugin.video.themoviedb.helper/'
ADDONDATA = 'special://profile/addon_data/plugin.video.themoviedb.helper/'

_addonlogname = '[plugin.video.themoviedb.helper]\n'
_debuglogging = ADDON.getSettingBool('debug_logging')


def format_name(cache_name, *args, **kwargs):
    # Define a type whitelist to avoiding adding non-basic types like classes to cache name
    permitted_types = [unicode, int, float, str, bool]
    for arg in args:
        if type(arg) not in permitted_types:
            continue
        cache_name = u'{}/{}'.format(cache_name, arg) if cache_name else u'{}'.format(arg)
    for key, value in sorted(kwargs.items()):
        if type(value) not in permitted_types:
            continue
        cache_name = u'{}&{}={}'.format(cache_name, key, value) if cache_name else u'{}={}'.format(key, value)
    return cache_name


def format_folderpath(path, content='videos', affix='return', info=None, play='PlayMedia'):
    if not path:
        return
    if info == 'play':
        return u'{}({})'.format(play, path)
    if xbmc.getCondVisibility("Window.IsMedia"):
        return u'Container.Update({})'.format(path)
    return u'ActivateWindow({},{},{})'.format(content, path, affix)


def reconfigure_legacy_params(**kwargs):
    if 'type' in kwargs:
        kwargs['tmdb_type'] = kwargs.pop('type')
    if kwargs.get('tmdb_type') in ['season', 'episode']:
        kwargs['tmdb_type'] = 'tv'
    return kwargs


def viewitems(obj, **kwargs):
    """  from future
    Function for iterating over dictionary items with the same set-like
    behaviour on Py2.7 as on Py3.

    Passes kwargs to method."""
    func = getattr(obj, "viewitems", None)
    if not func:
        func = obj.items
    return func(**kwargs)


def md5hash(value):
    if sys.version_info.major != 3:
        return hashlib.md5(str(value)).hexdigest()
    value = str(value).encode()
    return hashlib.md5(value).hexdigest()


def kodi_log(value, level=0):
    try:
        if isinstance(value, list):
            v = ''
            for i in value:
                v = u'{}{}'.format(v, i) if v else u'{}'.format(i)
            value = v
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        logvalue = u'{0}{1}'.format(_addonlogname, value)
        if sys.version_info < (3, 0):
            logvalue = logvalue.encode('utf-8', 'ignore')
        if level == 2 and _debuglogging:
            xbmc.log(logvalue, level=xbmc.LOGINFO)
        elif level == 1:
            xbmc.log(logvalue, level=xbmc.LOGINFO)
        else:
            xbmc.log(logvalue, level=xbmc.LOGDEBUG)
    except Exception as exc:
        xbmc.log(u'Logging Error: {}'.format(exc), level=xbmc.LOGINFO)


def get_language():
    if ADDON.getSettingInt('language'):
        return LANGUAGES[ADDON.getSettingInt('language')]
    return 'en-US'


def get_mpaa_prefix():
    if ADDON.getSettingString('mpaa_prefix'):
        return u'{} '.format(try_decode(ADDON.getSettingString('mpaa_prefix')))
    return u''


CONVERSION_TABLE = {
    'media': {
        'movie': {
            'tmdb': {
                'type': 'movie'},
            'trakt': {
                'type': 'movie'},
            'ftv': {
                'type': 'movies'}
        },
        'tvshow': {
            'tmdb': {
                'type': 'tv'},
            'trakt': {
                'type': 'show'},
            'ftv': {
                'type': 'tv'}
        },
        'season': {
            'tmdb': {
                'type': 'season'},
            'trakt': {
                'type': 'season'},
            'ftv': {
                'type': 'tv'}
        },
        'episode': {
            'tmdb': {
                'type': 'episode'},
            'trakt': {
                'type': 'episode'},
            'ftv': {
                'type': 'tv'}
        },
        'actor': {
            'tmdb': {
                'type': 'person'}
        },
        'director': {
            'tmdb': {
                'type': 'person'}
        },
        'set': {
            'tmdb': {
                'type': 'collection'}
        }
    },
    'trakt': {
        'movie': {
            'tmdb': {
                'type': 'movie'}
        },
        'show': {
            'tmdb': {
                'type': 'tv'}
        },
        'season': {
            'tmdb': {
                'type': 'season'}
        },
        'episode': {
            'tmdb': {
                'type': 'episode'}
        },
        'person': {
            'tmdb': {
                'type': 'person'}
        }
    },
    'tmdb': {
        'movie': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [342]},
            'container': {
                'type': 'movies'},
            'trakt': {
                'type': 'movie'},
            'dbtype': {
                'type': 'movie'}
        },
        'tv': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [20343]},
            'container': {
                'type': 'tvshows'},
            'trakt': {
                'type': 'show'},
            'dbtype': {
                'type': 'tvshow'}
        },
        'person': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32172]},
            'container': {
                'type': 'actors'},
            'dbtype': {
                'type': 'video'}  # Needs to be video for info dialog as actors not accepted
        },
        'collection': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32187]},
            'container': {
                'type': 'sets'},
            'dbtype': {
                'type': 'set'}
        },
        'review': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32188]}
        },
        'keyword': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [21861]}
        },
        'network': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32189]},
            'container': {
                'type': 'studios'},
            'dbtype': {
                'type': 'studio'}
        },
        'studio': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32190]},
            'container': {
                'type': 'studios'},
            'dbtype': {
                'type': 'studio'}
        },
        'image': {
            'plural': {
                'func': ADDON.getLocalizedString, 'args': [32191]},
            'container': {
                'type': 'images'}
        },
        'genre': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [135]},
            'container': {
                'type': 'genres'},
            'dbtype': {
                'type': 'genre'}
        },
        'season': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [33054]},
            'container': {
                'type': 'seasons'},
            'trakt': {
                'type': 'season'},
            'dbtype': {
                'type': 'season'}
        },
        'episode': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [20360]},
            'container': {
                'type': 'episodes'},
            'trakt': {
                'type': 'episode'},
            'dbtype': {
                'type': 'episode'}
        },
        'video': {
            'plural': {
                'func': xbmc.getLocalizedString, 'args': [10025]},
            'container': {
                'type': 'videos'},
            'dbtype': {
                'type': 'video'}
        },
    }
}


def _convert_types(base, key, output):
    info = CONVERSION_TABLE.get(base, {}).get(key, {}).get(output, {})
    if 'type' in info:
        return info['type']
    if 'func' in info:
        return info['func'](*info.get('args', []))
    return ''


def convert_media_type(media_type, output='tmdb', parent_type=False, strip_plural=False):
    if strip_plural:  # Strip trailing "s" from container_content to convert to media_type
        media_type = re.sub('s$', '', media_type)
    if parent_type and media_type in ['season', 'episode']:
        media_type = 'tvshow'
    return _convert_types('media', media_type, output)


def convert_trakt_type(trakt_type, output='tmdb'):
    return _convert_types('trakt', trakt_type, output)


def convert_type(tmdb_type, output, season=None, episode=None):
    if output == 'library':
        if tmdb_type == 'image':
            return 'pictures'
        return 'video'
    if tmdb_type == 'tv' and season is not None:
        tmdb_type == 'episode' if episode is not None else 'season'
    return _convert_types('tmdb', tmdb_type, output)
