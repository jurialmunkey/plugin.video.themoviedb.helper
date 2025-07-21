from tmdbhelper.lib.script.sync.trakt.item import ItemSync
from tmdbhelper.lib.addon.dialog import busy_decorator
from jurialmunkey.ftools import cached_property


class ItemProgress(ItemSync):
    preconfigured = True
    localized_name = 38209
    allow_episodes = True

    @cached_property
    def playback_id(self):
        return self.get_playback_id()

    def get_playback_id(self):
        if self.trakt_type == 'movie':
            return self.trakt_syncdata.get_movie_playprogress_id(self.tmdb_id)
        if self.season is None or self.episode is None:
            return
        return self.trakt_syncdata.get_episode_playprogress_id(self.tmdb_id, self.season, self.episode)

    def get_self(self):
        return self if self.playback_id else None

    @busy_decorator
    def get_sync_response(self):
        """ Called after user selects choice """
        return self.trakt_api.delete_response('sync', 'playback', self.playback_id)
