# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html


class DatabaseMaintenance:

    next_vacuum = 0
    next_delete = 0

    vacuum_interval = 60 * 60 * 6
    delete_interval = 60 * 60 * 24

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
        'blur',
        'crop',
        'desaturate',
        'colors'
    )

    def set_next_vacuum(self):
        from tmdbhelper.lib.addon.tmdate import set_timestamp
        self.next_vacuum = set_timestamp(self.vacuum_interval)

    def set_next_delete(self):
        from tmdbhelper.lib.addon.tmdate import set_timestamp
        self.next_delete = set_timestamp(self.delete_interval)

    def is_next_vacuum(self):
        from tmdbhelper.lib.addon.tmdate import get_timestamp
        return bool(not get_timestamp(self.next_vacuum))

    def is_next_delete(self):
        from tmdbhelper.lib.addon.tmdate import get_timestamp
        return bool(not get_timestamp(self.next_delete))

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
        if not force and not self.is_next_vacuum:
            return
        self.set_next_vacuum()
        from tmdbhelper.lib.addon.logger import TimerFunc
        from tmdbhelper.lib.items.database.database import ItemDetailsDatabase
        from tmdbhelper.lib.query.database.database import FindQueriesDatabase
        with TimerFunc('Vacuuming databases:', inline=True):
            ItemDetailsDatabase().execute_sql("VACUUM")
            FindQueriesDatabase().execute_sql("VACUUM")

    def delete_legacy_folders(self, force=False):
        """ Once-off routine to delete old unused database versions to avoid wasting disk space """
        if not force and not self.is_next_vacuum:
            return
        self.set_next_delete()
        from tmdbhelper.lib.files.futils import delete_folder
        for f in self.legacy_databases_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=True)
        for f in self.legacy_img_cache_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=True)
        for f in self.legacy_usr_cache_folders:
            delete_folder(f, force=True, check_exists=True, join_addon_data=False)

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
