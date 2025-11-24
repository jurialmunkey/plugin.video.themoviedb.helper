from tmdbhelper.lib.script.method.decorators import get_tmdb_id, map_kwargs


@map_kwargs({'play': 'tmdb_type'})
@get_tmdb_id
def play_player(ignore_default=False, allow_playlist=True, **kwargs):
    from jurialmunkey.parser import boolean
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.player.dialog.player import Player
    kodi_log(['play_player - attempting to play\n', kwargs], 1)
    player = Player(**kwargs)
    player.ignore_default = boolean(ignore_default)
    player.allow_playlist = boolean(allow_playlist)
    player.play()
