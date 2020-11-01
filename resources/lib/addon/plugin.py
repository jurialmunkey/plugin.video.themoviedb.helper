#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import xbmc
import xbmcaddon
import hashlib
from resources.lib.addon.constants import LANGUAGES
from resources.lib.addon.parser import try_decode


ADDON = xbmcaddon.Addon('plugin.video.themoviedb.helper')
ADDONPATH = ADDON.getAddonInfo('path')
PLUGINPATH = u'plugin://plugin.video.themoviedb.helper/'
ADDONDATA = 'special://profile/addon_data/plugin.video.themoviedb.helper/'

_addonlogname = '[plugin.video.themoviedb.helper]\n'
_debuglogging = ADDON.getSettingBool('debug_logging')


def format_folderpath(path, content='videos', affix='return', info=None):
    if not path:
        return
    if info == 'play':
        return u'PlayMedia({})'.format(path)
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
            xbmc.log(logvalue, level=xbmc.LOGNOTICE)
        elif level == 1:
            xbmc.log(logvalue, level=xbmc.LOGNOTICE)
        else:
            xbmc.log(logvalue, level=xbmc.LOGDEBUG)
    except Exception as exc:
        xbmc.log(u'Logging Error: {}'.format(exc), level=xbmc.LOGNOTICE)


def get_language():
    if ADDON.getSettingInt('language'):
        return LANGUAGES[ADDON.getSettingInt('language')]
    return 'en-US'


def get_mpaa_prefix():
    if ADDON.getSettingString('mpaa_prefix'):
        return u'{} '.format(try_decode(ADDON.getSettingString('mpaa_prefix')))
    return u''


def convert_media_type(media_type, output='tmdb', parent_type=False, strip_plural=False):
    if strip_plural:  # Strip trailing "s" from container_content to convert to media_type
        media_type = re.sub('s$', '', media_type)
    if output == 'tmdb':
        if media_type == 'movie':
            return 'movie'
        if media_type == 'tvshow':
            return 'tv'
        if media_type == 'season':
            return 'season' if not parent_type else 'tv'
        if media_type == 'episode':
            return 'episode' if not parent_type else 'tv'
        if media_type in ['actor', 'director']:
            return 'person'
        if media_type == 'sets':
            return 'collection'
    elif output == 'trakt':
        if media_type == 'movie':
            return 'movie'
        if media_type == 'tvshow':
            return 'show'
        if media_type == 'season':
            return 'season' if not parent_type else 'show'
        if media_type == 'episode':
            return 'episode' if not parent_type else 'show'
    elif output == 'ftv':
        if media_type == 'movie':
            return 'movies'
        if media_type in ['tvshow', 'season', 'episode']:
            return 'tv'


def convert_trakt_type(trakt_type, output='tmdb'):
    if output == 'tmdb':
        if trakt_type == 'movie':
            return 'movie'
        elif trakt_type == 'show':
            return 'tv'
        elif trakt_type == 'season':
            return 'season'
        elif trakt_type == 'episode':
            return 'episode'
        elif trakt_type == 'person':
            return 'person'


def convert_type(tmdb_type, output, season=None, episode=None):
    if tmdb_type == 'tv' and season is not None:
        tmdb_type == 'episode' if episode is not None else 'season'
    if output == 'plural':
        if tmdb_type == 'movie':
            return xbmc.getLocalizedString(342)
        elif tmdb_type == 'tv':
            return xbmc.getLocalizedString(20343)
        elif tmdb_type == 'person':
            return ADDON.getLocalizedString(32172)
        elif tmdb_type == 'collection':
            return ADDON.getLocalizedString(32187)
        elif tmdb_type == 'review':
            return ADDON.getLocalizedString(32188)
        elif tmdb_type == 'keyword':
            return xbmc.getLocalizedString(21861)
        elif tmdb_type == 'network':
            return ADDON.getLocalizedString(32189)
        elif tmdb_type == 'studio':
            return ADDON.getLocalizedString(32190)
        elif tmdb_type == 'image':
            return ADDON.getLocalizedString(32191)
        elif tmdb_type == 'genre':
            return xbmc.getLocalizedString(135)
        elif tmdb_type == 'season':
            return xbmc.getLocalizedString(33054)
        elif tmdb_type == 'episode':
            return xbmc.getLocalizedString(20360)
        elif tmdb_type == 'video':
            return xbmc.getLocalizedString(10025)
    elif output == 'container':
        if tmdb_type == 'movie':
            return 'movies'
        elif tmdb_type == 'tv':
            return 'tvshows'
        elif tmdb_type == 'person':
            return 'actors'
        elif tmdb_type == 'collection':
            return 'sets'
        elif tmdb_type == 'image':
            return 'images'
        elif tmdb_type == 'genre':
            return 'genres'
        elif tmdb_type == 'studio':
            return 'studios'
        elif tmdb_type == 'network':
            return 'studios'
        elif tmdb_type == 'season':
            return 'seasons'
        elif tmdb_type == 'episode':
            return 'episodes'
        elif tmdb_type == 'video':
            return 'videos'
    elif output == 'trakt':
        if tmdb_type == 'movie':
            return 'movie'
        elif tmdb_type == 'tv':
            return 'show'
        elif tmdb_type == 'season':
            return 'season'
        elif tmdb_type == 'episode':
            return 'episode'
    elif output == 'dbtype':
        if tmdb_type == 'movie':
            return 'movie'
        elif tmdb_type == 'tv':
            return 'tvshow'
        elif tmdb_type == 'person':
            return 'video'
        elif tmdb_type == 'collection':
            return 'set'
        elif tmdb_type == 'genre':
            return 'genre'
        elif tmdb_type == 'studio':
            return 'studio'
        elif tmdb_type == 'network':
            return 'studio'
        elif tmdb_type == 'season':
            return 'season'
        elif tmdb_type == 'episode':
            return 'episode'
        elif tmdb_type == 'video':
            return 'video'
    elif output == 'library':
        if tmdb_type == 'image':
            return 'pictures'
        else:
            return 'video'
    return ''
