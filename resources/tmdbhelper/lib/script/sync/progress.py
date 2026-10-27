from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.script.sync.item import ItemSync


class ItemProgress(ItemSync):
    preconfigured = True
    localized_name = 38209
    allow_episodes = True

    @cached_property
    def playback_id(self):
        return self.get_playback_id()

    def get_playback_id(self):
        if self.item_type == 'movie':
            return self.syncdata.get_movie_playprogress_id(self.tmdb_id)
        if self.season is None or self.episode is None:
            return
        return self.syncdata.get_episode_playprogress_id(self.tmdb_id, self.season, self.episode)

    def get_self(self):
        return self if self.playback_id else None
