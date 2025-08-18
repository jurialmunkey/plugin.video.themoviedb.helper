from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH, get_setting


class PlayerItemLocalMovie:

    kodi_dbtype = 'movie'

    def __init__(self, tmdb=None, imdb=None, tvdb=None, **kwargs):
        self.tmdb_id = tmdb
        self.imdb_id = imdb
        self.tvdb_id = tvdb

    @cached_property
    def is_enabled(self):
        return bool(get_setting('default_player_kodi', 'int'))

    @cached_property
    def kodi_db(self):
        if not self.is_enabled:
            return
        return KodiLibrary(dbtype=self.kodi_dbtype)

    @cached_property
    def kodi_dbid(self):
        if not self.kodi_db:
            return
        return self.kodi_db.get_info(
            'dbid',
            tmdb_id=self.tmdb_id,
            imdb_id=self.imdb_id,
            tvdb_id=self.tvdb_id,
        )

    @cached_property
    def kodi_file(self):
        if not self.kodi_dbid:
            return
        return self.kodi_db.get_info(
            'file',
            dbid=self.kodi_dbid
        )

    @cached_property
    def kodi_file_contents(self):
        if not self.kodi_file.endswith('.strm'):
            return
        from tmdbhelper.lib.files.futils import read_file
        return read_file(self.kodi_file)

    @cached_property
    def file(self):
        if not self.kodi_file:
            return
        if not self.kodi_file_contents:  # Not a .strm so send file
            return self.kodi_file
        if self.kodi_file_contents.startswith('plugin://plugin.video.themoviedb.helper'):  # Avoid recursive loop
            return
        return self.kodi_file_contents
        # if self.details:  # Add dbid to details to update our local progress.
        #     self.details.infolabels['dbid'] = dbid

    @cached_property
    def configured_item(self):
        if not self.file:
            return
        return {
            'name': f'{get_localized(32061)} Kodi',
            'is_folder': False,
            'is_local': True,
            'is_resolvable': "true",
            'make_playlist': "true",
            'plugin_name': 'xbmc.core',
            'plugin_icon': f'{ADDONPATH}/resources/icons/other/kodi.png',
            'actions': self.file
        }


class PlayerItemLocalEpisode(PlayerItemLocalMovie):

    kodi_dbtype = 'tvshow'

    def __init__(self, season=None, episode=None, **kwargs):
        super().__init__(**kwargs)
        self.season = season
        self.episode = episode

    @cached_property
    def kodi_db_episodes(self):
        if not self.kodi_dbid:
            return
        return KodiLibrary(dbtype='episode', tvshowid=self.kodi_dbid)

    @cached_property
    def kodi_file(self):
        if not self.kodi_db_episodes:
            return
        return self.kodi_db_episodes.get_info('file', season=self.season, episode=self.episode)
