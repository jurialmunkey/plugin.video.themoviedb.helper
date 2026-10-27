from hashlib import sha256
from os import makedirs
from os.path import join
from sqlite3 import OperationalError, connect
from time import monotonic
from xbmc import Monitor
from xbmcvfs import translatePath
from jurialmunkey.ftools import cached_property


class SQLiteMutex:
    """ Hold a named SQLite transaction; lockstate is the name, or -1 on abort/timeout. """

    def __init__(self, name, timeout=10, polling=0.05, kodi_log=None):
        self.name = name
        self.timeout = timeout
        self.polling = polling
        self.kodi_log = kodi_log
        self.connection = connect(self.path, timeout=0, isolation_level=None)
        try:
            self.lockstate = self.acquire()
        except BaseException:
            self.connection.close()
            raise
        if self.lockstate == -1:
            self.connection.close()

    @cached_property
    def monitor(self):
        return Monitor()

    @cached_property
    def path(self):
        return self.get_path()

    def get_path(self):
        folder = translatePath('special://temp/tmdbhelper/locks/')
        makedirs(folder, exist_ok=True)
        filename = sha256(self.name.encode('utf-8')).hexdigest()
        return join(folder, f'{filename}.db')

    def acquire(self):
        deadline = monotonic() + self.timeout
        while not self.monitor.abortRequested():
            try:
                self.connection.execute('BEGIN IMMEDIATE')
                return self.name
            except OperationalError as exc:
                if str(exc) != 'database is locked':
                    raise
            remaining = deadline - monotonic()
            if remaining <= 0:
                if self.kodi_log is not None:
                    self.kodi_log(f'{self.name} Timeout!', 1)
                return -1
            self.monitor.waitForAbort(min(self.polling, remaining))
        return -1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lockstate == -1:
            return
        try:
            self.connection.rollback()
        finally:
            self.connection.close()
