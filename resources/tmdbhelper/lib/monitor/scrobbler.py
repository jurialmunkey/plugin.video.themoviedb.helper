from jurialmunkey.window import get_property
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_setting
from tmdbhelper.lib.addon.logger import kodi_log
from tmdbhelper.lib.addon.tmdate import set_timestamp


class PlayerScrobbler():
    def __init__(self, total_time, provider, syncdata):
        self.provider = provider
        self.syncdata = syncdata
        self.start_time = 0
        self.frozen_time = None
        self.total_time = total_time
        self.tvdb_id = self.playerstring.get('tvdb_id')
        self.imdb_id = self.playerstring.get('imdb_id')
        self.tmdb_id = self.playerstring.get('tmdb_id')
        self.tmdb_type = self.playerstring_get_tmdb_type()
        self.season = int(self.playerstring.get('season') or 0)
        self.episode = int(self.playerstring.get('episode') or 0)
        self.stopped = False
        self.started = False
        self.syncing = False

    def playerstring_get_tmdb_type(self):
        tmdb_type = self.playerstring.get('tmdb_type')
        if tmdb_type in ('movie', ):
            return 'movie'
        if tmdb_type in ('season', 'episode', 'tv'):
            return 'tv'
        return ''

    @cached_property
    def request(self):
        return self.get_request()

    def get_request(self):
        if self.provider is not None and self.provider.is_authorized():
            return self.provider.scrobbler_class(self, self.provider)

    @cached_property
    def playback_refresh(self):
        return self.get_playback_refresh()

    def get_playback_refresh(self):
        from tmdbhelper.lib.monitor.playback_refresh import PlaybackRefreshFactory
        return PlaybackRefreshFactory(self.provider, self.syncdata)

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
    def current_time(self):
        if self.frozen_time is not None:
            return self.frozen_time
        return set_timestamp(-self.start_time)

    @current_time.setter
    def current_time(self, value):
        self.start_time = set_timestamp(-value)
        if self.frozen_time is not None:
            self.frozen_time = value

    @is_scrobbling
    def freeze_time(self):
        self.frozen_time = self.current_time

    @is_scrobbling
    def resume_time(self):
        self.start_time = set_timestamp(-self.current_time)
        self.frozen_time = None

    @property
    def progress(self):
        return ((self.current_time / self.total_time) * 100)

    @cached_property
    def playerstring(self):
        from tmdbhelper.lib.player.action.playerstring import read_playerstring
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
        # kodi_log(f'SCROBBLER: [UPDATE] {self.content_id} -- {self.progress:.2f}%', 2)

    @is_scrobbling
    def start(self, tmdb_type, tmdb_id, paused=False):
        if not self.is_match(tmdb_type, tmdb_id):
            return
        if paused:
            self.freeze_time()
        else:
            self.resume_time()
        if self.started or self.stopped:
            return self.sync(tmdb_type, tmdb_id)
        self.scrobble('start')
        self.started = True

    @is_scrobbling
    def pause(self, tmdb_type, tmdb_id):
        if not self.is_match(tmdb_type, tmdb_id):
            return
        self.freeze_time()
        return self.sync(tmdb_type, tmdb_id)  # Pauses still check the completion threshold.

    @is_scrobbling
    def stop(self, tmdb_type, tmdb_id):
        if not self.started or self.stopped:
            return
        self.freeze_time()
        kodi_log(f'SCROBBLER: [Stop] {self.content_id} -- {self.progress:.2f}%', 2)
        self.scrobble('stop') if not self.syncing else None
        self.set_tmdb_ratings()
        self.stopped = True

    @is_scrobbling
    def sync(self, tmdb_type, tmdb_id):
        if self.syncing:
            return
        if not self.started or self.stopped:
            return
        if self.progress < 80:
            return
        if not self.is_match(tmdb_type, tmdb_id):
            return
        result = self.scrobble('stop')
        self.syncing = result is None or result.successful

    @is_scrobbling
    def scrobble(self, method):
        if method not in ('start', 'stop') or self.request is None:
            return
        if not self.provider.is_authorized():
            return
        result = self.request.scrobble(method)
        if result.successful and method == 'stop':
            self.playback_refresh.refresh(result.history_changed, sync=self.progress >= 80)
        return result

    @is_scrobbling
    def set_tmdb_ratings(self):
        if not get_setting('tmdb_user_token', 'str'):
            return
        if not get_setting('tmdb_user_rate_after_watching'):
            return
        if not self.current_time:
            return
        # Only update if progress is 80% or more
        if self.progress < 80:
            return
        if self.content_id == get_property('Scrobbler.LastRated.ContentID'):
            return
        get_property('Scrobbler.LastRated.ContentID', set_property=self.content_id)
        from tmdbhelper.lib.script.sync.menu_default import sync_item
        kodi_log(f'SCROBBLER: [Rate] {self.content_id}', 2)
        sync_item(
            tmdb_type=self.tmdb_type,
            tmdb_id=self.tmdb_id,
            season=self.season or None,
            episode=self.episode or None,
            sync_type='tmdbrating'
        )


def PlayerScrobblerFactory(total_time):
    from tmdbhelper.lib.sync.datasync import SyncDataFactory
    from tmdbhelper.lib.monitor.scrobblers import PlayerScrobblers
    syncdata = SyncDataFactory()
    providers = syncdata.registry.get_selected_providers('scrobbling')
    return PlayerScrobblers(total_time, providers, syncdata)
