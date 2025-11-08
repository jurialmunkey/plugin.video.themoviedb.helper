from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.items.media import LibraryMedia


class LibraryEpisode(LibraryMedia):
    @cached_property
    def number(self):
        return self.infolabels.get_key('episode') or 0

    @cached_property
    def season(self):
        return self.infolabels.get_key('season') or 0

    @cached_property
    def filename(self):
        from jurialmunkey.parser import try_int
        from tmdbhelper.lib.files.futils import validify_filename
        return validify_filename(f'S{try_int(self.season):02d}E{try_int(self.number):02d} - {self.title}')
