from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.update.builder.media import LibraryBuilderMedia


class LibraryBuilderMovies(LibraryBuilderMedia):
    tmdb_type = 'movie'

    @cached_property
    def library_item_class(self):
        from tmdbhelper.lib.update.items.movie import LibraryMovie
        return LibraryMovie
