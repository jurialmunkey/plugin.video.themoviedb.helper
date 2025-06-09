def get_details(self, trakt_type, trakt_id, season=None, episode=None, extended='full'):
    if season is None or episode is None:
        return self.get_request_lc(f'{trakt_type}s', trakt_id, extended=extended)
    return self.get_request_lc(f'{trakt_type}s', trakt_id, 'seasons', season, 'episodes', episode, extended=extended)
