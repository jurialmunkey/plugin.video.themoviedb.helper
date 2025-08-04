from jurialmunkey.window import get_property
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.addon.logger import kodi_log


class PlayerScrobbler():
    def __init__(self, trakt_api, total_time):
        self.trakt_api = trakt_api
        self.current_time = 0
        self.total_time = total_time
        self.tvdb_id = self.playerstring.get('tvdb_id')
        self.imdb_id = self.playerstring.get('imdb_id')
        self.tmdb_id = self.playerstring.get('tmdb_id')
        self.tmdb_type = self.playerstring_get_tmdb_type()
        self.season = int(self.playerstring.get('season') or 0)
        self.episode = int(self.playerstring.get('episode') or 0)
        self.stopped = False
        self.started = False

    def playerstring_get_tmdb_type(self):
        tmdb_type = self.playerstring.get('tmdb_type')
        if tmdb_type in ('movie', ):
            return 'movie'
        if tmdb_type in ('season', 'episode', 'tv'):
            return 'tv'
        return ''

    def is_trakt_authorized(func):
        """ decorator to check that trakt is authorized  """

        def wrapper(self, *args, **kwargs):
            if not get_property('TraktIsAuth', is_type=float):
                return
            if not get_setting('trakt_scrobbling'):
                return
            if not self.trakt_api.is_authorized:
                return
            if not self.trakt_item:
                return
            return func(self, *args, **kwargs)

        return wrapper

    def is_scrobbling(func):
        """ decorator to check if available item should be scrobbled """

        def wrapper(self, *args, **kwargs):
            if self.stopped:
                return
            if not self.tmdb_type:
                return
            if not self.tmdb_id:
                return
            if not self.total_time:
                return
            return func(self, *args, **kwargs)

        return wrapper

    @property
    def content_id(self):
        return f'{self.tmdb_type}.{self.tmdb_id}.{self.season}.{self.episode}'

    @property
    def progress(self):
        return ((self.current_time / self.total_time) * 100)

    @cached_property
    def playerstring(self):
        from tmdbhelper.lib.player.details.playerstring import read_playerstring
        return read_playerstring()

    def is_match(self, tmdb_type, tmdb_id):
        if f'{self.tmdb_id}' != f'{tmdb_id}':
            return False
        if f'{self.tmdb_type}' != f'{tmdb_type}':
            return False
        return True

    @is_scrobbling
    def update_time(self, tmdb_type, tmdb_id, current_time):
        if not self.is_match(tmdb_type, tmdb_id):
            return
        self.current_time = current_time

    @cached_property
    def trakt_item(self):
        return self.get_trakt_item() or {}

    @is_scrobbling
    def get_trakt_item(self):
        if self.tmdb_type == 'tv':
            if not self.season or not self.episode:
                return
            return {
                'show': {'ids': {'tmdb': self.tmdb_id}},
                'episode': {'season': self.season, 'number': self.episode},
                'progress': self.progress
            }

        if self.tmdb_type == 'movie':
            return {
                'movie': {'ids': {'tmdb': self.tmdb_id}},
                'progress': self.progress
            }

    @is_scrobbling
    @is_trakt_authorized
    def trakt_scrobbling(self, method):
        if method not in ('start', 'pause', 'stop'):
            return
        self.trakt_item['progress'] = self.progress
        self.trakt_api.get_api_request(
            f'https://api.trakt.tv/scrobble/{method}',
            postdata=self.trakt_item,
            headers=self.trakt_api.headers,
            method='json'
        )

    @is_scrobbling
    def start(self, tmdb_type, tmdb_id):
        if not self.is_match(tmdb_type, tmdb_id):
            return self.stop(tmdb_type, tmdb_id)
        kodi_log(f'SCROBBLER: [Start] {self.content_id}', 2)
        self.trakt_scrobbling('start')
        self.started = True

    @is_scrobbling
    def pause(self, tmdb_type, tmdb_id):
        if not self.is_match(tmdb_type, tmdb_id):
            return self.stop(tmdb_type, tmdb_id)
        kodi_log(f'SCROBBLER: [Pause] {self.content_id}', 2)
        self.trakt_scrobbling('pause')

    @is_scrobbling
    def stop(self, tmdb_type, tmdb_id):
        if not self.started:
            return
        kodi_log(f'SCROBBLER: [Stop] {self.content_id}', 2)
        self.trakt_scrobbling('stop')
        self.set_kodi_watched()
        self.set_tmdb_ratings()
        self.update_stats()
        # TODO: Decide if we allow further scrobbling of item if restarted after stopped
        # if self.is_match(tmdb_type, tmdb_id):
        #     return
        self.stopped = True

    @is_scrobbling
    @is_trakt_authorized
    def update_stats(self):
        from tmdbhelper.lib.script.method.trakt import get_stats
        from tmdbhelper.lib.addon.consts import LASTACTIVITIES_DATA
        get_property(LASTACTIVITIES_DATA, clear_property=True)
        get_stats()

    @is_scrobbling
    def set_tmdb_ratings(self):
        if not get_setting('tmdb_user_token', 'str'):
            return
        if not get_setting('tmdb_user_rate_after_watching'):
            return
        if not self.current_time:
            return
        # Only update if progress is 75% or more
        if self.progress < 75:
            return
        if self.content_id == get_property('Scrobbler.LastRated.ContentID'):
            return
        get_property('Scrobbler.LastRated.ContentID', set_property=self.content_id)
        from tmdbhelper.lib.script.sync.tmdb.menu import sync_item
        kodi_log(f'SCROBBLER: [Rate] {self.content_id}', 2)
        sync_item(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season or None,
            episode=self.episode or None,
            sync_type='rating'
        )

    @is_scrobbling
    def set_kodi_watched(self):
        if not self.current_time:
            return
        # Only update if progress is 75% or more
        if self.progress < 75:
            return

        import tmdbhelper.lib.api.kodi.rpc as rpc

        if self.tmdb_type == 'tv':
            tvshowid = rpc.KodiLibrary('tvshow').get_info(
                info='dbid',
                imdb_id=self.imdb_id,
                tmdb_id=self.tmdb_id,
                tvdb_id=self.tvdb_id)
            if not tvshowid:
                kodi_log(f'SCROBBLER: [Kodi] No SHOW: {self.content_id}', 2)
                return
            dbid = rpc.KodiLibrary('episode', tvshowid).get_info(
                info='dbid',
                season=self.season,
                episode=self.episode)
            if not dbid:
                kodi_log(f'SCROBBLER: [Kodi] No DBID: {self.content_id}', 2)
                return
            rpc.set_watched(dbid=dbid, dbtype='episode')
            kodi_log(f'SCROBBLER: [Kodi] {self.content_id}', 2)
            return

        if self.tmdb_type == 'movie':
            dbid = rpc.KodiLibrary('movie').get_info(
                info='dbid',
                imdb_id=self.imdb_id,
                tmdb_id=self.tmdb_id,
                tvdb_id=self.tvdb_id)
            if not dbid:
                kodi_log(f'SCROBBLER: [Kodi] No DBID: {self.content_id}', 2)
                return
            rpc.set_watched(dbid=dbid, dbtype='movie')
            kodi_log(f'SCROBBLER: [Kodi] {self.content_id}', 2)
            return
