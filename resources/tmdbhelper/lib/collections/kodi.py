"""Kodi paths and lifecycle boundary for the standalone collection index."""
from pathlib import Path
from xbmcvfs import translatePath
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONDATA, get_setting
from tmdbhelper.lib.collections.database import DATABASE_PATH
from tmdbhelper.lib.collections.runtime_database import CollectionIndex
from tmdbhelper.lib.files.sqlite_mutex import SQLiteMutex
from tmdbhelper.lib.addon.logger import kodi_log
import sqlite3


class KodiCollectionIndex(CollectionIndex):
    def initialise(self):
        with SQLiteMutex('collections.initialise', timeout=30) as lock:
            if lock.lockstate == -1:
                raise sqlite3.OperationalError('Collection index initialisation stopped or timed out')
            super().initialise()


def get_collection_index():
    filename = Path(translatePath(f'{ADDONDATA}collections/collections.db'))
    return KodiCollectionIndex(filename, DATABASE_PATH)


class CollectionMaintenance:
    def __init__(self, abort=None):
        self.abort = abort

    @cached_property
    def index(self):
        return self.get_index()

    @staticmethod
    def get_index():
        return get_collection_index()

    @cached_property
    def api_key(self):
        return self.get_api_key()

    @staticmethod
    def get_api_key():
        from tmdbhelper.lib.api.api_keys.tmdb import API_KEY
        return API_KEY

    @property
    def enabled(self):
        # No maintenance until the list has created its profile-local index.
        return bool(get_setting('nextmovies_updates') and self.api_key and self.index.filename.exists())

    @cached_property
    def updater(self):
        return self.get_updater()

    def get_updater(self):
        from xbmc import Monitor
        from tmdbhelper.lib.collections.updater import CollectionUpdater
        return CollectionUpdater(
            self.index, self.api_key, daily_limit=get_setting('nextmovies_daily_budget', 'int'),
            abort=self.abort or Monitor().abortRequested)

    def run(self):
        if not self.enabled:
            return
        with SQLiteMutex('collections.maintenance', timeout=0) as lock:
            if lock.lockstate == -1:
                return
            self.run_update()

    def run_update(self):
        from tmdbhelper.lib.collections.client import CollectionAPIError
        try:
            self.updater.run()
        except (CollectionAPIError, OSError, sqlite3.Error) as error:
            kodi_log(f'Collection index maintenance: {type(error).__name__}: {error}', 1)


def update_collection_index(abort=None):
    CollectionMaintenance(abort=abort).run()
