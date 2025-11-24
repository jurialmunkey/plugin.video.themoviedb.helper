# from tmdbhelper.lib.addon.logger import kodi_log
# from tmdbhelper.lib.addon.plugin import get_localized
# from tmdbhelper.lib.api.kodi.rpc import set_tags
# from tmdbhelper.lib.update.common import LibraryCommon
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import set_tags
from tmdbhelper.lib.update.builder.userlist import LibraryBuilderUserList
from tmdbhelper.lib.update.builder.media import LibraryBuilder


class LibraryTagsMedia:

    kodidb = None
    item_type = None
    tags = ()

    LOG_LEVEL_WARN = 1
    LOG_LEVEL_FAIL = 2
    LOG_STATUS_EXISTED = 1
    LOG_STATUS_NO_DBID = 2
    LOG_STATUS_SUCCESS = 0

    @cached_property
    def log_status(self):
        if not self.dbid:
            return self.LOG_STATUS_NO_DBID
        if not self.is_tagged:
            return self.LOG_STATUS_EXISTED
        return self.LOG_STATUS_SUCCESS

    @cached_property
    def log_message(self):
        log_message = {
            self.LOG_STATUS_SUCCESS: 'successfully tagged',
            self.LOG_STATUS_EXISTED: 'item already tagged',
            self.LOG_STATUS_NO_DBID: 'error locating item in library',
        }
        return log_message[self.log_status]

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
    def dbid(self):
        return self.get_kodi_info('dbid')

    def get_kodi_info(self, info, **kwargs):
        return self.kodidb.get_info(info=info, imdb_id=self.imdb_id, tmdb_id=self.tmdb_id)

    @cached_property
    def is_tagged(self):
        return set_tags(self.dbid, self.item_type, tags=self.tags)


class LibraryTagsMovie(LibraryTagsMedia):
    item_type = 'movie'
    tmdb_type = 'movie'


class LibraryTagsTvshow(LibraryTagsMedia):
    item_type = 'tvshow'
    tmdb_type = 'tv'


class LibraryBuilderTagsMedia:
    tmdb_type = None
    play_type = None

    @cached_property
    def tags(self):
        return (f'Trakt User {self.user_slug}', f'Trakt List {self.list_slug}')

    def add_item(self, library_item):
        return self.logger.add(
            library_item.tmdb_type,
            tmdb_id=library_item.tmdb_id,
            user_slug=self.user_slug,
            list_slug=self.list_slug,
            log_msg=library_item.log_message,
        )

    library_item_class = None

    def create(self, tmdb_id=None, imdb_id=None, **kwargs):
        library_item = self.library_item_class()
        library_item.tmdb_id = tmdb_id
        library_item.imdb_id = imdb_id
        library_item.tags = self.tags
        library_item.kodidb = self.kodidb[self.tmdb_type]
        self.add_item(library_item)

    playlist_filepath = 'special://profile/playlists/video/'

    @cached_property
    def playlist_filename(self):
        return f'{self.user_slug}-{self.list_slug}-{self.play_type}'

    @cached_property
    def playlist_contents(self):
        fcontent = [u'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>']
        fcontent.append(f'<smartplaylist type="{self.play_type}">')
        fcontent.append(f'    <name>{self.list_slug} by {self.user_slug} ({self.play_type})</name>')
        fcontent.append(u'    <match>all</match>')
        fcontent.append(f'    <rule field="tag" operator="is"><value>Trakt User {self.user_slug}</value></rule>')
        fcontent.append(f'    <rule field="tag" operator="is"><value>Trakt List {self.list_slug}</value></rule>')
        fcontent.append(u'</smartplaylist>')
        return '\n'.join(fcontent)

    def create_playlist(self):
        from tmdbhelper.lib.update.filewriter import FileWriter
        filewriter = FileWriter(self.playlist_filepath, self.playlist_filename, content=self.playlist_contents)
        filewriter.file_extension = 'xsp'
        filewriter.clean_url = False
        return filewriter.success


class LibraryBuilderTagsMovies(LibraryBuilderTagsMedia):
    tmdb_type = 'movie'
    play_type = 'movies'
    library_item_class = LibraryTagsMovie


class LibraryBuilderTagsTvshows(LibraryBuilderTagsMedia):
    tmdb_type = 'tv'
    play_type = 'tvshows'
    library_item_class = LibraryTagsTvshow


class LibraryBuilderTagsUserList(LibraryBuilderUserList):

    is_overlimit = False
    is_confirmed = True  # Tagger auto runs so dont interrupt to ask permission

    @cached_property
    def builder_tvshows(self):
        return self.get_builder(LibraryBuilderTagsTvshows())

    @cached_property
    def builder_movies(self):
        return self.get_builder(LibraryBuilderTagsMovies())

    def get_builder(self, builder):
        builder = super().get_builder(builder)
        builder.user_slug = self.user_slug
        builder.list_slug = self.list_slug
        return builder

    def create_playlists(self):
        if self.len_movies > 0:
            self.builder_movies.create_playlist()
        if self.len_tvshows > 0:
            self.builder_tvshows.create_playlist()


class LibraryBuilderTags(LibraryBuilder):
    log_folder = 'log_tagger'
    dialog_top = 'TMDbHelper Tagger'

    @property
    def auto_update(self):
        return False

    @property
    def clean_library(self):
        return False

    @cached_property
    def dialog_txt(self):
        from tmdbhelper.lib.addon.plugin import get_localized
        return f'{get_localized(32167)}...'

    @cached_property
    def request(self):
        from tmdbhelper.lib.update.monitor import MonitorUserLists
        return MonitorUserLists().monitored_lists

    def create(self, **kwargs):
        if not self.request:
            return

        total = len(self.request)

        # Tag items
        for count, (list_slug, user_slug) in enumerate(self.request):
            self.dialog_msg(count, total, message=f'Tagging {list_slug} ({user_slug})...')
            builder = self.get_builder(LibraryBuilderTagsUserList())
            builder.create(user_slug=user_slug, list_slug=list_slug)
            builder.create_playlists()


def library_tagger(*args, **kwargs):
    with LibraryBuilderTags(*args, **kwargs) as library_tagger:
        library_tagger.create()
