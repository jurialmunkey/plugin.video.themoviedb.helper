from tmdbhelper.lib.script.sync.item import ItemSync
from tmdbhelper.lib.addon.dialog import BusyDialog


class ItemProgressAttributes:
    """
    playback_id
    """
    @property
    def playback_id(self):
        try:
            return self._playback_id
        except AttributeError:
            self._playback_id = self.get_playback_id()
            return self._playback_id

    @playback_id.setter
    def playback_id(self, value):
        self._playback_id = value

    def get_playback_id(self):
        if self.trakt_type == 'movie':
            return self.trakt_syncdata.get_movie_playprogress_id(self.tmdb_id)
        if self.season is None or self.episode is None:
            return
        return self.trakt_syncdata.get_episode_playprogress_id(self.tmdb_id, self.season, self.episode)


class ItemProgress(ItemSync, ItemProgressAttributes):
    preconfigured = True
    localized_name = 38209
    allow_episodes = True

    def get_self(self):
        if not self.playback_id:
            return
        return self

    def get_sync_response(self):
        """ Called after user selects choice """
        with BusyDialog():
            data = self.trakt_api.delete_response('sync', 'playback', self.playback_id)
        return data
