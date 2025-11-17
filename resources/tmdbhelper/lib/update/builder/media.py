from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.common import LibraryCommon


class LibraryBuilder(LibraryCommon):

    log_folder = 'log_library'
    dialog_top = 'TMDbHelper Library'
    library_item_class = None
    tmdb_type = None

    @cached_property
    def dialog_txt(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        return get_localized(32166)

    @cached_property
    def auto_update(self):
        from tmdbhelper.lib.addon.plugin import get_setting
        return get_setting('auto_update')

    def get_builder(self, instance):
        instance.kodidb = self.kodidb
        instance.logger = self.logger
        instance.dialog = self.dialog
        instance.forced = self.forced
        return instance


class LibraryBuilderMedia(LibraryBuilder):
    def add_library_item(self, library_item, log_msg):
        return self.logger.add(
            library_item.tmdb_type,
            season=library_item.season,
            episode=library_item.episode,
            tmdb_id=library_item.tmdb_id,
            log_msg=log_msg,
        )

    def set_library_item(self, library_item):
        self.add_library_item(library_item, library_item.log_message)

    def get_library_item(self, tmdb_id):
        library_item = self.library_item_class(tmdb_id)
        library_item.kodidb = self.kodidb[self.tmdb_type]
        return library_item

    def create(self, tmdb_id, **kwargs):
        return self.set_library_item(self.get_library_item(tmdb_id))
