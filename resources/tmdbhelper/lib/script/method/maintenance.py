# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from jurialmunkey.ftools import cached_property


MAINTENANCE_CACHE = 'Maintenance.db'


class MaintenanceSchedule:
    """ Persist when a maintenance task is next due so the schedule survives Kodi restarts """

    cache_name = None
    interval = None

    def __init__(self, cache):
        self.cache = cache

    @property
    def cache_days(self):
        from jurialmunkey.scache import TIME_DAYS
        return self.interval / TIME_DAYS

    @property
    def next_run(self):
        return self.get_next_run()

    def get_next_run(self):
        return self.cache.get_cache(self.cache_name)

    @property
    def is_due(self):
        return not self.next_run

    def set_next(self):
        from tmdbhelper.lib.addon.tmdate import set_timestamp
        self.cache.set_cache(set_timestamp(self.interval, True), cache_name=self.cache_name, cache_days=self.cache_days)


class VacuumSchedule(MaintenanceSchedule):
    cache_name = 'DatabaseMaintenance.vacuum'
    interval = 60 * 60 * 6


class DeleteLegacySchedule(MaintenanceSchedule):
    cache_name = 'DatabaseMaintenance.delete_legacy_folders'
    interval = 60 * 60 * 24


class ImageCleanupSchedule(MaintenanceSchedule):
    cache_name = 'DatabaseMaintenance.prune_image_cache'
    interval = 60 * 60 * 2


class DatabaseMaintenance:

    allow_during_video_playback = False

    legacy_databases_folders = (
        'database',
        'database_v2',
        'database_v3',
        'database_v4',
        'database_v5',
        'database_v6',
        'database_v7'
    )

    legacy_img_cache_folders = (
        'blur', 'blur_v2',
        'crop',
        'desaturate',
        'colors'
    )

    @cached_property
    def maintenance_cache(self):
        return self.get_maintenance_cache()

    def get_maintenance_cache(self):
        from tmdbhelper.lib.files.bcache import BasicCache
        return BasicCache(MAINTENANCE_CACHE)

    @cached_property
    def vacuum_schedule(self):
        return self.get_vacuum_schedule()

    def get_vacuum_schedule(self):
        return VacuumSchedule(self.maintenance_cache)

    @cached_property
    def delete_schedule(self):
        return self.get_delete_schedule()

    def get_delete_schedule(self):
        return DeleteLegacySchedule(self.maintenance_cache)

    @cached_property
    def image_cleanup_schedule(self):
        return self.get_image_cleanup_schedule()

    def get_image_cleanup_schedule(self):
        return ImageCleanupSchedule(self.maintenance_cache)

    @property
    def is_blocked_by_playback(self):
        if self.allow_during_video_playback:
            return False
        import xbmc
        return xbmc.Player().isPlayingVideo()

    @property
    def is_vacuum_allowed(self):
        if self.is_blocked_by_playback:
            return False
        return self.vacuum_schedule.is_due

    @property
    def is_delete_allowed(self):
        if self.is_blocked_by_playback:
            return False
        return self.delete_schedule.is_due

    @property
    def is_image_cleanup_allowed(self):
        if self.is_blocked_by_playback:
            return False
        return self.image_cleanup_schedule.is_due

    @property
    def legacy_usr_cache_folders(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        image_location = get_setting('image_location', 'str')
        return tuple((
            f'{image_location}{f}'
            for f in self.legacy_img_cache_folders
        )) if image_location else tuple()

    @property
    def todays_date(self):
        from tmdbhelper.lib.addon.tmdate import get_todays_date
        return get_todays_date()

    def vacuum(self, force=False):
        if not force and not self.is_vacuum_allowed:
            return
        self.vacuum_schedule.set_next()
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with TimerFunc('Vacuuming databases:', inline=True):
            ItemDetailsDatabase().execute_sql("VACUUM")
            FindQueriesDatabase().execute_sql("VACUUM")

    def delete_legacy_folders(self, force=False):
        """ Once-off routine to delete old unused database versions to avoid wasting disk space """
        if not force and not self.is_delete_allowed:
            return
        self.delete_schedule.set_next()
        from tmdbhelper.lib.files.futils import delete_folder
        for f in self.legacy_databases_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=True)
        for f in self.legacy_img_cache_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=True)
        for f in self.legacy_usr_cache_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=False)

    def prune_image_cache(self):
        if not self.is_image_cleanup_allowed:
            return
        self.image_cleanup_schedule.set_next()
        from tmdbhelper.lib.files.imagecache import ImageCacheMaintenance
        ImageCacheMaintenance().prune()

    @staticmethod
    def recache_kodidb(notification=True, confirmation=False):
        from tmdbhelper.lib.addon.plugin import ADDONPATH
        from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
        from tmdbhelper.lib.addon.logger import TimerFunc
        from xbmcgui import Dialog

        with TimerFunc('KodiLibrary sync took', inline=True):
            KodiLibrary('movie', cache_refresh=True)
            KodiLibrary('tvshow', cache_refresh=True)

        if notification:
            head = 'TMDbHelper'
            data = 'Kodi Library cached to memory'
            icon = f'{ADDONPATH}/icon.png'
            Dialog().notification(head, data, icon=icon)

        if confirmation:
            head = 'TMDbHelper'
            data = 'Kodi Library cached to memory'
            Dialog().ok(head, data)


recache_kodidb = DatabaseMaintenance.recache_kodidb
