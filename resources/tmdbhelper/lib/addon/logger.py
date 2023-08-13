import jurialmunkey.logger as jurialmunkey_logger
from timeit import default_timer as timer
from tmdbhelper.lib.addon.plugin import get_setting, format_name, get_localized


LOGGER = jurialmunkey_logger.Logger(
    log_name='[plugin.video.themoviedb.helper]\n',
    notification_head=f'TheMovieDb Helper {get_localized(257)}',
    notification_text=get_localized(2104),
    debug_logging=get_setting('debug_logging'))
kodi_log = LOGGER.kodi_log
kodi_traceback = LOGGER.kodi_traceback
kodi_try_except = LOGGER.kodi_try_except
log_timer_report = LOGGER.log_timer_report
TimerList = jurialmunkey_logger.TimerList
TimerFunc = jurialmunkey_logger.TimerFunc


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
