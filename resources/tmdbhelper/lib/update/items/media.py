from jurialmunkey.ftools import cached_property


class LibraryMedia:

    cache = None

    tmdb_type = ''
    strm_fstr = ''

    skip_future = True
    skip_nodate = True

    is_added = False

    def __init__(self, tmdb_id):
        self.tmdb_id = tmdb_id

    @cached_property
    def basedir(self):
        from tmdbhelper.lib.update.common import LibraryCommon
        return LibraryCommon.get_basedir(self.base_type)

    def set_cache(self, key, value):
        if not self.cache:
            return
        if not key or not value:
            return
        if isinstance(self.cache.my_history[key], list):
            self.cache.my_history[key].append(value)
        if isinstance(self.cache.my_history[key], int):
            from jurialmunkey.parser import try_int
            self.cache.my_history[key] = try_int(value)

    """
    Kodi Data
    """
    @cached_property
    def kodidb(self):
        from tmdbhelper.lib.update.common import LibraryCommon
        return LibraryCommon.get_kodidb(self.tmdb_type)

    def get_kodi_info(self, *args, **kwargs):
        return self.kodidb.get_info(*args, **kwargs)

    """
    Sync Data
    """

    @cached_property
    def sync(self):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory(self.mediatype)
        sync.tmdb_id = self.tmdb_id
        return sync

    @cached_property
    def sync_data(self):
        return self.key_getter(self.sync.data)

    def key_getter(self, dictionary):
        from tmdbhelper.lib.addon.plugin import KeyGetter
        return KeyGetter(dictionary)

    @cached_property
    def infolabels(self):
        infolabels = self.sync_data.get_key('infolabels')
        return self.key_getter(infolabels)

    @cached_property
    def unique_ids(self):
        unique_ids = self.sync_data.get_key('unique_ids')
        return self.key_getter(unique_ids)

    """
    Meta Data
    """

    @cached_property
    def imdb_id(self):
        return self.unique_ids.get_key('imdb')

    @cached_property
    def tvdb_id(self):
        return self.unique_ids.get_key('tvdb')

    @cached_property
    def premiered(self):
        return self.infolabels.get_key('premiered')

    @cached_property
    def title(self):
        return self.infolabels.get_key('title')

    @cached_property
    def tvshowtitle(self):
        return self.infolabels.get_key('tvshowtitle')

    season = None
    episode = None

    @cached_property
    def year(self):
        return self.premiered[:4] if self.premiered else None

    @cached_property
    def is_future_premiere(self):
        if not self.skip_future:
            return False
        from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp
        return is_unaired_timestamp(self.premiered, self.skip_nodate)

    """
    File Data
    """

    @cached_property
    def name(self):
        return self.get_name()

    def get_name(self):
        if not self.title:
            return
        name = f'{self.title} ({self.year})' if self.year else self.title
        return self.get_unique_name(name)

    def get_unique_name(self, name):
        from jurialmunkey.parser import try_int
        from tmdbhelper.lib.files.futils import get_tmdb_id_nfo
        condition = try_int(get_tmdb_id_nfo(self.basedir, name))
        condition = bool(condition and condition != try_int(self.tmdb_id))
        return f'{name} (TMDB {self.tmdb_id})' if condition else name

    @cached_property
    def file(self):
        file = self.library_file
        file = file or self.strm_file
        return file or ''

    @cached_property
    def strm_file(self):
        if self.log_status:
            return
        if not self.strm_filewriter:
            return
        return self.strm_filewriter.filename_and_path

    @cached_property
    def folders(self):
        return [self.name]

    library_file = None

    LOG_STATUS_SUCCESS = 0
    LOG_STATUS_LIBRARY = 1

    LOG_LEVEL_WARN = 2
    LOG_STATUS_UNAIRED = 2

    LOG_LEVEL_FAIL = 3
    LOG_STATUS_NO_STRM = 3
    LOG_STATUS_NO_INFO = 4
    LOG_STATUS_UNKNOWN = 5
    LOG_STATUS_NO_FILE = 6
    LOG_STATUS_NO_PATH = 7
    LOG_STATUS_NO_DATA = 8
    LOG_STATUS_XBMCVFS = 9

    @cached_property
    def log_message(self):
        log_message = {
            self.LOG_STATUS_SUCCESS: 'successfully added',
            self.LOG_STATUS_LIBRARY: 'skipped item in library',
            self.LOG_STATUS_UNAIRED: 'skipped item is unaired',
            self.LOG_STATUS_NO_STRM: 'error writing file',
            self.LOG_STATUS_NO_INFO: 'error writing info',
            self.LOG_STATUS_UNKNOWN: 'error unknown',
            self.LOG_STATUS_NO_FILE: 'error making valid filename',
            self.LOG_STATUS_NO_PATH: 'error making valid filepath',
            self.LOG_STATUS_NO_DATA: 'error making valid strmdata',
            self.LOG_STATUS_XBMCVFS: 'error making new folder',
        }
        return f'{log_message[self.log_status]} {self.name}'

    @cached_property
    def log_error(self):
        if self.log_status < self.LOG_LEVEL_FAIL:
            return
        return self.log_message

    @cached_property
    def log_warning(self):
        if self.log_status < self.LOG_LEVEL_WARN:
            return
        return self.log_message

    @cached_property
    def log_status(self):
        if self.library_file:
            return self.LOG_STATUS_LIBRARY
        if self.is_future_premiere:
            return self.LOG_STATUS_UNAIRED
        if self.strm_filewriter and not self.strm_filewriter.success:
            if self.strm_filewriter.error == self.strm_filewriter.ERROR_FILENAME:
                return self.LOG_STATUS_NO_FILE
            if self.strm_filewriter.error == self.strm_filewriter.ERROR_FILEPATH:
                return self.LOG_STATUS_NO_PATH
            if self.strm_filewriter.error == self.strm_filewriter.ERROR_CONTENTS:
                return self.LOG_STATUS_NO_DATA
            if self.strm_filewriter.error == self.strm_filewriter.ERROR_MAKEPATH:
                return self.LOG_STATUS_XBMCVFS
            return self.LOG_STATUS_NO_STRM
        if self.info_filewriter and not self.info_filewriter.success:
            return self.LOG_STATUS_NO_INFO
        return self.LOG_STATUS_SUCCESS

    """
    STRM File
    """

    @cached_property
    def strm_filewriter(self):
        if not self.strm_filename:
            return
        if not self.strm_contents:
            return
        from tmdbhelper.lib.update.filewriter import FileWriter
        filewriter = FileWriter(self.basedir, *self.folders, self.strm_filename, content=self.strm_contents)
        return filewriter

    @cached_property
    def strm_filename(self):
        return self.name

    @cached_property
    def strm_contents(self):
        if not self.tmdb_id:
            return
        return self.strm_fstr.format(tmdb_id=self.tmdb_id)

    """
    INFO File
    """

    @cached_property
    def info_filewriter(self):
        if not self.info_filename:
            return
        if not self.info_contents:
            return
        from tmdbhelper.lib.update.filewriter import FileWriter
        filewriter = FileWriter(self.basedir, *self.folders, self.info_filename, content=self.info_contents)
        filewriter.file_extension = 'nfo'
        filewriter.clean_url = False
        return filewriter

    @cached_property
    def info_filename(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        if get_setting('alternative_nfo'):
            return f'{self.mediatype}-tmdbhelper'
        return self.mediatype

    @cached_property
    def info_contents(self):
        return f'https://www.themoviedb.org/{self.tmdb_type}/{self.tmdb_id}'
