from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.tmdate import is_unaired_timestamp


class FloppyAiredEpisodes:
    """ Aired episodes of a show or one season from TMDb used to mark a whole show or season on Floppy """

    def __init__(self, tmdb_id, season=None):
        self.tmdb_id = tmdb_id
        self.season = season

    @cached_property
    def tmdb_api(self):
        from tmdbhelper.lib.api.tmdb.api import TMDb
        return TMDb()

    @cached_property
    def season_numbers(self):
        return self.get_season_numbers()

    def get_season_numbers(self):
        if self.season is not None:
            return [self.season]
        details = self.tmdb_api.get_request_sc('tv', self.tmdb_id) or {}
        return [i['season_number'] for i in details.get('seasons') or [] if i['season_number']]  # Skip specials

    def get_season_episodes(self, season):
        details = self.tmdb_api.get_request_sc('tv', self.tmdb_id, 'season', season) or {}
        return [
            (season, i['episode_number'])
            for i in details.get('episodes') or []
            if not is_unaired_timestamp(i.get('air_date'))
        ]

    @cached_property
    def items(self):
        return [j for i in self.season_numbers for j in self.get_season_episodes(i)]
