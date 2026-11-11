class MonitorPartialRatings:
    """An item's ratings for a monitor, as each set of its providers finishes.

    Each set has every value so far, so that it replaces the set before it. The item detail
    service is asked again until it has every provider. Asking again stops when is_current()
    reports that the monitor has moved on, so that the next item is not held up.
    """

    def __init__(self, lidc, tmdb_type, tmdb_id, season=None, episode=None, is_current=None):
        self.lidc = lidc
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.season = season
        self.episode = episode
        self.is_current = is_current

    def get_reply(self, received):
        return self.lidc.get_ratings(self.tmdb_type, self.tmdb_id, self.season, self.episode, received=received, awards=True)

    def __iter__(self):
        reply = {'received': 0, 'complete': False}
        while not reply['complete'] and self.is_current():
            reply = self.get_reply(reply['received'])
            yield reply['ratings']
