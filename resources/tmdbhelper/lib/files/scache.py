#!/usr/bin/python
# -*- coding: utf-8 -*-
import jurialmunkey.scache
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.files.futils import FileUtils
from tmdbhelper.lib.files.dbdata import DATABASE_NAME


class SimpleCache(jurialmunkey.scache.SimpleCache):
    _basefolder = get_setting('cache_location', 'str') or ''
    _fileutils = FileUtils()  # Import to use plugin addon_data folder not the module one

    @staticmethod
    def kodi_log(msg, level=0):
        kodi_log(msg, level)

    def __init__(self, folder=None, filename=None):
        folder = folder or DATABASE_NAME
        super().__init__(folder=folder, filename=filename)
