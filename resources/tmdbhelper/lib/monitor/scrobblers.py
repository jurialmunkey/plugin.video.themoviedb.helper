from tmdbhelper.lib.monitor.scrobbler import PlayerScrobbler


class PlayerProviderScrobbler(PlayerScrobbler):
    def set_tmdb_ratings(self):
        # The coordinator owns the single rating prompt for this playback.
        return


class PlayerScrobblers:
    def __init__(self, total_time, providers, syncdata):
        self.scrobblers = tuple(
            PlayerProviderScrobbler(total_time, provider, syncdata) for provider in providers)
        self.ratings = PlayerScrobbler(total_time, None, syncdata)

    @property
    def players(self):
        return (*self.scrobblers, self.ratings)

    def update_time(self, tmdb_type, tmdb_id, current_time):
        for player in self.players:
            player.update_time(tmdb_type, tmdb_id, current_time)

    def start(self, tmdb_type, tmdb_id):
        for player in self.players:
            player.start(tmdb_type, tmdb_id)

    def pause(self, tmdb_type, tmdb_id):
        for player in self.players:
            player.pause(tmdb_type, tmdb_id)

    def stop(self, tmdb_type, tmdb_id):
        for player in self.players:
            player.stop(tmdb_type, tmdb_id)

    def sync(self, tmdb_type, tmdb_id):
        for player in self.players:
            player.sync(tmdb_type, tmdb_id)
