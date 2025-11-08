from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.tvshow import LibraryTvshow


class LibraryLegacyConversion(LibraryTvshow):

    @cached_property
    def basedir_validated(self):
        return self.basedir.replace('\\', '/')

    def get_folder(self, folder):
        from tmdbhelper.lib.files.futils import validify_filename
        return f'{self.basedir_validated}{validify_filename(folder)}/'

    @cached_property
    def new_folder(self):
        return self.get_folder(self.name)

    def rename(self, folder):
        if not folder:
            return
        if not self.name:
            return
        if folder == self.name:
            return
        from xbmcvfs import rename
        rename(self.get_folder(folder), self.new_folder)
