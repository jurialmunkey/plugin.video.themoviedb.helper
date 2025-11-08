from jurialmunkey.ftools import cached_property


class LibraryMedia:

    library_file = None
    sync_type = ''
    strm_fstr = ''
    basedir = ''

    def __init__(self, tmdb_id, force=False):
        self.tmdb_id = tmdb_id
        self.force = force

    """
    Sync Data
    """

    @cached_property
    def sync(self):
        from tmdbhelper.lib.items.database.baseitem_factories.factory import BaseItemFactory
        sync = BaseItemFactory(self.sync_type)
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
    def year(self):
        return self.premiered[:4] if self.premiered else None

    @cached_property
    def name(self):
        return self.get_name(self.title, self.year)

    def get_name(self, name, year=None):
        if not name:
            return
        from tmdbhelper.lib.update.update import get_unique_folder
        name = f'{name} ({year})' if year else name
        return get_unique_folder(name, self.tmdb_id, self.basedir)

    """
    File Data
    """

    @cached_property
    def file_contents(self):
        if not self.tmdb_id:
            return
        return self.strm_fstr.format(self.tmdb_id)

    @cached_property
    def file(self):
        file = self.library_file
        file = file or self.create_new_file()
        return file or ''

    @cached_property
    def log_message(self):
        if self.library_file:
            return 'item in library'
        if self.file:
            return 'added strm file'
        return ''

    def create_new_file(self):
        if not self.file_contents:
            return
        file = self.make_file()
        self.make_nfo()
        return file

    def make_file(self):
        from tmdbhelper.lib.update.update import create_file
        file = create_file(self.file_contents, self.name, self.name, basedir=self.basedir)
        return file

    def make_nfo(self):
        from tmdbhelper.lib.update.update import create_nfo
        create_nfo(self.sync_type, self.tmdb_id, self.name, basedir=self.basedir)

    @cached_property
    def playlist_rule(self):
        return ('filename', self.file.replace('\\', '/').split('/')[-1])
