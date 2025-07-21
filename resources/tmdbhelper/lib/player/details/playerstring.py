from jurialmunkey.ftools import cached_property


class PlayerStringMovie:
    tmdb_type = 'movie'
    tvdb_id = None

    def __init__(self, listitem):
        self.listitem = listitem

    @cached_property
    def tmdb_id(self):
        return self.listitem.getProperty('tmdb_id') or self.listitem_infotag.getUniqueID('tmdb')

    @cached_property
    def imdb_id(self):
        return self.listitem_infotag.getUniqueID('imdb')

    @cached_property
    def listitem_infotag(self):
        return self.listitem.getVideoInfoTag()

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
        return self.get_playerstring()

    def get_playerstring(self):
        if not self.tmdb_id:
            return
        from json import dumps
        return dumps(self.playerstring_meta)


class PlayerStringEpisode(PlayerStringMovie):
    tmdb_type = 'episode'

    @cached_property
    def season(self):
        return self.listitem_infotag.getSeason()

    @cached_property
    def episode(self):
        return self.listitem_infotag.getEpisode()

    @cached_property
    def tmdb_id(self):
        return self.listitem.getProperty('tmdb_id') or self.listitem_infotag.getUniqueID('tvshow.tmdb')

    @cached_property
    def imdb_id(self):
        return self.listitem_infotag.getUniqueID('tvshow.imdb')

    @cached_property
    def tvdb_id(self):
        return self.listitem_infotag.getUniqueID('tvshow.tvdb')

    def get_playerstring_meta(self):
        meta = super().get_playerstring_meta()
        meta['season'] = self.season
        meta['episode'] = self.episode
        return meta

    def get_playerstring(self):
        if self.season in (None, '', 0, -1):
            return
        if self.episode in (None, '', 0, -1):
            return
        return super().get_playerstring()


def make_playerstring(listitem):
    try:
        tmdb_type = listitem.getProperty('tmdb_type')
    except (KeyError, AttributeError, TypeError):
        return
    if tmdb_type in ('episode', 'tv'):
        return PlayerStringEpisode(listitem).playerstring
    if tmdb_type == 'movie':
        return PlayerStringMovie(listitem).playerstring


def read_playerstring():
    from json import loads
    from jurialmunkey.window import get_property
    playerstring = get_property('PlayerInfoString')
    return loads(playerstring) if playerstring else {}
