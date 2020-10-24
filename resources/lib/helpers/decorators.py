import xbmc
from contextlib import contextmanager
from resources.lib.helpers.plugin import kodi_log
from resources.lib.helpers.cache import format_name
from timeit import default_timer as timer


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
