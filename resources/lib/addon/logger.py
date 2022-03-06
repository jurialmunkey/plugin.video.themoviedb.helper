import xbmc
import traceback
from timeit import default_timer as timer
from resources.lib.addon.plugin import get_setting, format_name


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


def kodi_log_traceback(exception, log_msg=None, log_level=1):
    """ Method for logging caught exceptions and notifying user """
    msg = f'Error Type: {type(exception).__name__}\nError Contents: {exception.args!r}'
    msg = [log_msg, '\n', msg, '\n'] if log_msg else [msg, '\n']
    try:
        kodi_log(msg + traceback.format_tb(exception.__traceback__), log_level)
    except Exception as exc:
        kodi_log(f'ERROR WITH TRACEBACK!\n{exc}\n{msg}', log_level)


class TryExceptLog():
    def __init__(self, exc_types=[Exception], log_msg=None, log_level=1):
        """ ContextManager to allow exception passing and log """
        self.log_msg = log_msg
        self.exc_types = exc_types
        self.log_level = log_level

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type and exc_type not in self.exc_types:
            return
        if self.log_level:
            kodi_log(f'{self.log_msg or "ERROR PASSED"}: {exc_type}', self.log_level)
        return True


def timer_report(func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            """ Syntactic sugar to time a class function """
            timer_a = timer()
            response = func(self, *args, **kwargs)
            timer_z = timer()
            total_time = timer_z - timer_a
            if total_time > 0.001:
                timer_name = f'{self.__class__.__name__}.{func_name}.'
                timer_name = format_name(timer_name, *args, **kwargs)
                kodi_log(f'{timer_name}\n{total_time:.3f} sec', 1)
            return response
        return wrapper
    return decorator


def log_output(func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            """ Syntactic sugar to log output of function """
            response = func(self, *args, **kwargs)
            log_text = f'{self.__class__.__name__}.{func_name}.'
            log_text = format_name(log_text, *args, **kwargs)
            kodi_log(log_text, 1)
            kodi_log(response, 1)
            return response
        return wrapper
    return decorator


class TimerFunc():
    def __init__(self, timer_name, log_threshold=0.001):
        """ ContextManager for timing code blocks and outputing to log """
        self.timer_name = timer_name
        self.log_threshold = log_threshold
        self.timer_a = timer()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        timer_z = timer()
        total_time = timer_z - self.timer_a
        if total_time > self.log_threshold:
            kodi_log(f'{self.timer_name}\n{total_time:.3f} sec', 1)


class TimerList():
    def __init__(self, dict_obj, list_name, log_threshold=0.001, logging=True):
        """ ContextManager for timing code blocks and storing in a list """
        self.list_obj = dict_obj.setdefault(list_name, [])
        self.log_threshold = log_threshold
        self.timer_a = timer() if logging else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not self.timer_a:
            return
        timer_z = timer()
        total_time = timer_z - self.timer_a
        if total_time > self.log_threshold:
            self.list_obj.append(total_time)
