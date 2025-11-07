from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.api.kodi.rpc import KodiLibrary
from tmdbhelper.lib.addon.plugin import get_localized, ADDONPATH, get_setting
from tmdbhelper.lib.player.dialog.item.basic import PlayerItemBasic


class PlayerItemLocalMovie(PlayerItemBasic):

    kodi_dbtype = 'movie'

    def __init__(self, item=None):
        self.item = item

    @cached_property
    def tmdb_id(self):
        return self.item.get('tmdb')

    @cached_property
    def imdb_id(self):
        return self.item.get('imdb')

    @cached_property
    def tvdb_id(self):
        return self.item.get('tvdb')

    @cached_property
    def is_enabled(self):
        return bool(get_setting('default_player_kodi', 'int'))

    @cached_property
    def is_strm(self):
        return bool(self.kodi_file.endswith('.strm'))

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
        return self.kodi_db.get_info('file', dbid=self.kodi_dbid)

    @cached_property
    def kodi_file_contents(self):
        if not self.is_strm:
            return
        from tmdbhelper.lib.files.futils import read_file
        return read_file(self.kodi_file)

    @cached_property
    def actions(self):
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
    def name(self):
        return f'{get_localized(32061)} Kodi'

    is_folder = False
    is_local = True
    is_resolvable = True
    is_provider = 0
    make_playlist = False
    requires_ids = False
    plugin_name = 'xbmc.core'
    plugin_icon = f'{ADDONPATH}/resources/icons/other/kodi.png'
    file = ''
    mode = ''
    fallback = ''


class PlayerItemLocalEpisode(PlayerItemLocalMovie):

    kodi_dbtype = 'tvshow'
    make_playlist = True

    @cached_property
    def season(self):
        return self.item.get('season')

    @cached_property
    def episode(self):
        return self.item.get('episode')

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
