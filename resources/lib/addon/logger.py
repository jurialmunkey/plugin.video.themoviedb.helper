import xbmc
import traceback
from resources.lib.addon.dialog import kodi_notification
from resources.lib.addon.plugin import get_localized, get_setting


ADDON_LOGNAME = '[plugin.video.themoviedb.helper]\n'
DEBUG_LOGGING = get_setting('debug_logging')


def kodi_log(value, level=0):
    try:
        if isinstance(value, list):
            value = ''.join(map(str, value))
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        logvalue = f'{ADDON_LOGNAME}{value}'
        if level == 2 and DEBUG_LOGGING:
            xbmc.log(logvalue, level=xbmc.LOGINFO)
        elif level == 1:
            xbmc.log(logvalue, level=xbmc.LOGINFO)
        else:
            xbmc.log(logvalue, level=xbmc.LOGDEBUG)
    except Exception as exc:
        xbmc.log(f'Logging Error: {exc}', level=xbmc.LOGINFO)


def kodi_traceback(exception, log_msg=None, notification=True, log_level=1):
    if notification:
        head = f'TheMovieDb Helper {get_localized(257)}'
        kodi_notification(head, get_localized(2104))
    msg = f'Error Type: {type(exception).__name__}\nError Contents: {exception.args!r}'
    msg = [log_msg, '\n', msg, '\n'] if log_msg else [msg, '\n']
    try:
        kodi_log(msg + traceback.format_tb(exception.__traceback__), log_level)
    except Exception as exc:
        kodi_log(f'ERROR WITH TRACEBACK!\n{exc}\n{msg}', log_level)
