# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
from jurialmunkey.ftools import cached_property


class PlayUsing:
    def __init__(
        self,
        player,
        mode=None,
        tmdb_type=None,
        tmdb_id=None,
        imdb_id=None,
        season=None,
        episode=None,
        ep_year=None,
        year=None,
        query=None,
        **kwargs,
    ):
        self.player = player
        self.mode = mode or 'play'
        self.tmdb_type = tmdb_type
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.season = season
        self.episode = episode
        self.ep_year = ep_year
        self.year = year
        self.query = query

    keys = (
        'tmdb_type',
        'tmdb_id',
        'imdb_id',
        'season',
        'episode',
        'ep_year',
        'year',
        'query',
    )

    @cached_property
    def focused_listitem(self):
        if self.tmdb_type:
            return
        from tmdbhelper.lib.script.method.focused_listitem import FocusedListItem
        return FocusedListItem()

    @cached_property
    def params(self):
        params = self.get_params()
        params = self.set_focused_listitem_params(params)
        params['player'] = self.player
        params['mode'] = self.mode
        return params

    def get_params(self):
        return {
            key: value for key, value in (
                (k, getattr(self, k, None))
                for k in self.keys
            ) if value
        }

    def set_focused_listitem_params(self, params):
        if not self.focused_listitem:
            return params
        params.update(self.focused_listitem.params)
        params.update({
            key: value for key, value in (
                (k, getattr(self.focused_listitem, k, None))
                for k in self.keys
            ) if value and key not in params
        })
        return params

    def play(self):
        from tmdbhelper.lib.script.method.play_player import play_player
        play_player(**self.params)


def play_using(play_using, **kwargs):
    return PlayUsing(player=play_using, **kwargs).play()
