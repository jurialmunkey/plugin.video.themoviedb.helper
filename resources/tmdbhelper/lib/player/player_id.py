from jurialmunkey.ftools import cached_property


class PlayerIdMovie:
    affix = 'movie'

    def __init__(self, player=None, mode=None):
        self.player = player
        self.mode = mode or 'play'

    @cached_property
    def prefix(self):
        if not self.player:
            return ''
        return f'{self.player} {self.mode}'

    @cached_property
    def player_id(self):
        if not self.prefix:
            return ''
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
