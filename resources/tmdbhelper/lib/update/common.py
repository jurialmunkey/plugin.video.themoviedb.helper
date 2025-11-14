from jurialmunkey.ftools import cached_property


class LibraryCommon():
    busy_spinner = True
    clean_library = False
    debug_logging = True
    auto_update = False
    forced = False

    """
    Basedir
    """

    @staticmethod
    def get_basedir(mediatype):
        from tmdbhelper.lib.addon.plugin import get_setting
        basedir = get_setting(f'{mediatype}_library', 'str')
        basedir = basedir or f'special://profile/addon_data/plugin.video.themoviedb.helper/{mediatype}/'
        return basedir

    @staticmethod
    def get_listdir_basedir(basedir):
        from xbmcvfs import listdir
        from tmdbhelper.lib.files.futils import get_tmdb_id_nfo
        return [
            i for i in (
                (get_tmdb_id_nfo(basedir, f), f)
                for f in listdir(basedir)[0]
            ) if i[0] and i[1]
        ]

    """
    Logging
    """

    @cached_property
    def logger(self):
        from tmdbhelper.lib.update.logger import LibraryLogger
        logger = LibraryLogger()
        logger.location = self.log_folder
        return logger

    @cached_property
    def dialog(self):
        from xbmcgui import DialogProgressBG
        dialog = DialogProgressBG()
        dialog.create(self.dialog_top, self.dialog_txt)
        return dialog

    def dialog_msg(self, count, total, **kwargs):
        if not self.dialog:
            return
        self.dialog.update((((count + 1) * 100) // total), **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        from tmdbhelper.lib.addon.plugin import executebuiltin
        for func in (
            func for func, cond in (
                (lambda: self.dialog.close(), self.dialog),
                (lambda: self.logger.out(), self.debug_logging),
                (lambda: executebuiltin('UpdateLibrary(video)'), self.auto_update),
                (lambda: executebuiltin('ClearLibrary(video)'), self.clean_library),
            ) if cond
        ):
            func()

    """
    Kodi DB
    """
    @cached_property
    def kodidb(self):

        class KodiDBDictionary(dict):
            def __missing__(instance, key):
                instance[key] = self.get_kodidb(key)
                return instance[key]

        return KodiDBDictionary()

    @staticmethod
    def get_kodidb(library):
        from tmdbhelper.lib.api.kodi.rpc import get_kodi_library
        return get_kodi_library(library, cache_refresh=True)
