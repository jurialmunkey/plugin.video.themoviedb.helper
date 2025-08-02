from jurialmunkey.ftools import cached_property


class PlayerIdMovie:
    affix = 'movie'

    def __init__(self, player=None, mode=None):
        self.player = player
        self.mode = mode or 'play'

    @cached_property
    def prefix(self):
        return f'{self.player} {self.mode}' if self.player else ''

    @cached_property
    def player_id(self):
        return f'{self.prefix}_{self.affix}'


class PlayerIdEpisode(PlayerIdMovie):
    affix = 'episode'


def PlayerId(tmdb_type, player=None, mode=None):
    routes = {
        'movie': PlayerIdMovie,
        'tv': PlayerIdEpisode,
        'episode': PlayerIdEpisode,
    }
    return routes[tmdb_type](player, mode)
