from jurialmunkey.locker import MutexPropLock
from tmdbhelper.lib.addon.logger import kodi_log


def mutexlock(func):
    def wrapper(self, *args, **kwargs):
        mutex_lockname = self.mutex_lockname
        with MutexPropLock(mutex_lockname, timeout=300, kodi_log=kodi_log) as mutex_lock:
            if mutex_lock.lockstate == -1:  # Abort or Timeout
                return
            return func(self, *args, **kwargs)
    return wrapper


def mutexlock_funcname(func):
    def wrapper(self, *args, **kwargs):
        mutex_lockname = f'{func.__name__}.{args}.{self.mutex_lockname}'
        with MutexPropLock(mutex_lockname, timeout=300, kodi_log=kodi_log) as mutex_lock:
            if mutex_lock.lockstate == -1:  # Abort or Timeout
                return
            return func(self, *args, **kwargs)
    return wrapper
