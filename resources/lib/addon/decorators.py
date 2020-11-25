import xbmc
import xbmcgui
import traceback
from contextlib import contextmanager
from resources.lib.addon.plugin import kodi_log, format_name
from timeit import default_timer as timer


def try_except_log(log_msg, notification=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if notification:
                    head = 'TheMovieDb Helper {}'.format(xbmc.getLocalizedString(257))
                    xbmcgui.Dialog().notification(head, xbmc.getLocalizedString(2104))
                msg = 'Error Type: {0}\nError Contents: {1!r}'
                msg = msg.format(type(exc).__name__, exc.args)
                kodi_log([log_msg, '\n', msg, '\n'] + traceback.format_tb(exc.__traceback__), 1)
        return wrapper
    return decorator


@contextmanager
def busy_dialog(is_enabled=True):
    if is_enabled:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        if is_enabled:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def busy_decorator(func):
    def wrapper(*args, **kwargs):
        with busy_dialog:
            response = func(*args, **kwargs)
        return response
    return wrapper


def timer_report(func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            """ Syntactic sugar to time a class function """
            timer_a = timer()
            response = func(self, *args, **kwargs)
            timer_z = timer()
            total_time = timer_z - timer_a
            if total_time > 0.001:
                timer_name = '{}.{}.'.format(self.__class__.__name__, func_name)
                timer_name = format_name(timer_name, *args, **kwargs)
                kodi_log('{}\n{:.3f} sec'.format(timer_name, total_time), 1)
            return response
        return wrapper
    return decorator


def log_output(func_name):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            """ Syntactic sugar to log output of function """
            response = func(self, *args, **kwargs)
            log_text = '{}.{}.'.format(self.__class__.__name__, func_name)
            log_text = format_name(log_text, *args, **kwargs)
            kodi_log(log_text, 1)
            kodi_log(response, 1)
            return response
        return wrapper
    return decorator
