from tmdbhelper.lib.script.method.decorators import get_tmdb_id, map_kwargs


@map_kwargs({'play': 'tmdb_type'})
@get_tmdb_id
def play_external(folder_path=None, reset_focus=None, ignore_default=False, **kwargs):
    from tmdbhelper.lib.addon.logger import kodi_log
    from tmdbhelper.lib.player.players import PlayersFactory
    kodi_log(['play_external - attempting to play\n', kwargs], 1)
    PlayersFactory(**kwargs).play(
        folder_path=folder_path,
        reset_focus=reset_focus,
        ignore_default=ignore_default
    )
