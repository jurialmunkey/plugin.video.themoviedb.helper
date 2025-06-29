from tmdbhelper.lib.files.ftools import cached_property


class PlayerStringMovie:
    tmdb_type = 'movie'
    tvdb_id = None

    def __init__(self, tmdb_id, details):
        self.tmdb_id = tmdb_id
        self.details = details

    def details_get(self, attr, key):
        try:
            return getattr(self.details, attr)[key]
        except (AttributeError, KeyError, TypeError):
            return

    @cached_property
    def imdb_id(self):
        return self.details_get('unique_ids', 'imdb')

    @cached_property
    def playerstring_meta(self):
        return self.get_playerstring_meta()

    def get_playerstring_meta(self):
        playerstring_meta = {
            k: v for k, v in (
                ('tmdb_type', self.tmdb_type),
                ('tmdb_id', self.tmdb_id),
                ('imdb_id', self.imdb_id),
                ('tvdb_id', self.tvdb_id),
            ) if v
        }
        return playerstring_meta

    @cached_property
    def playerstring(self):
        from json import dumps
        return dumps(self.playerstring_meta)


class PlayerStringEpisode(PlayerStringMovie):
    tmdb_type = 'episode'

    def __init__(self, tmdb_id, details, season, episode):
        self.tmdb_id = tmdb_id
        self.details = details
        self.season = season
        self.episode = episode

    @cached_property
    def imdb_id(self):
        return self.get_details('unique_ids', 'tvshow.imdb')

    @cached_property
    def tvdb_id(self):
        return self.get_details('unique_ids', 'tvshow.tvdb')

    def get_meta(self):
        meta = super().get_meta()
        meta['season'] = self.season
        meta['episode'] = self.episode
        return meta


def make_playerstring(tmdb_type, tmdb_id, details=None, season=None, episode=None):
    if tmdb_type in ('episode', 'tv') and season is not None and episode is not None:
        return PlayerStringEpisode(tmdb_id, details, season, episode).playerstring
    if tmdb_type == 'movie':
        return PlayerStringMovie(tmdb_id, details).playerstring


def read_playerstring():
    from json import loads
    from jurialmunkey.window import get_property
    playerstring = get_property('PlayerInfoString')
    return loads(playerstring) if playerstring else {}
