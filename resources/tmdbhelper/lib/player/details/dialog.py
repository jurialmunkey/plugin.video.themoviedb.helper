from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.player.details.item import PlayerItemConstructed
from tmdbhelper.lib.player.details.kodi import PlayerItemLocalMovie, PlayerItemLocalEpisode


class PlayersDialogMovie:
    tmdb_type = 'movie'
    mode_type = 'movie'
    local_item_class = PlayerItemLocalMovie

    def __init__(self, item, data):
        self.item = item  # Details about playable item
        self.data = data  # Players list data - usually self.players_prioritised

    def get_player_generator(self, mode):
        return (
            PlayerItemConstructed(file=file, item=self.item, mode=mode, meta=meta)
            for file, meta in self.data
        )

    def get_configured_players(self, mode):
        return [
            i.configured_item
            for i in self.get_player_generator(mode)
            if i.configured_item
        ]

    @cached_property
    def items_play_local(self):
        items_play_local = self.local_item_class(**self.item).configured_item
        return [items_play_local] if items_play_local else []

    @cached_property
    def items_play(self):
        return self.items_play_local + self.get_configured_players(f'play_{self.mode_type}')

    @cached_property
    def items_search(self):
        return self.get_configured_players(f'search_{self.mode_type}')

    @cached_property
    def items(self):
        return self.items_play + self.items_search


class PlayersDialogEpisode(PlayersDialogMovie):
    tmdb_type = 'tv'
    mode_type = 'episode'
    local_item_class = PlayerItemLocalEpisode


def PlayersDialog(tmdb_type, *args, **kwargs):
    routes = {
        'movie': PlayersDialogMovie,
        'tv': PlayersDialogEpisode,
    }
    return routes[tmdb_type](*args, **kwargs)
