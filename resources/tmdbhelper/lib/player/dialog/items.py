from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.player.dialog.item.constructed import PlayerItemConstructed
from tmdbhelper.lib.player.dialog.item.kodi import PlayerItemLocalMovie, PlayerItemLocalEpisode


class PlayerItemsMovie:
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

    def get_players(self, mode):
        return [i for i in self.get_player_generator(mode) if i.is_valid]

    def del_player(self, player):
        for x, i in enumerate(self.items_play.copy()):
            if i == player:
                self.items_play.pop(x)
                return
        for x, i in enumerate(self.items_search.copy()):
            if i == player:
                self.items_search.pop(x)
                return

    @cached_property
    def items_play_local(self):
        items_play_local = self.local_item_class(item=self.item) if self.item else None
        if not items_play_local:
            return []
        if not items_play_local.is_valid:
            return []
        return [items_play_local]

    @cached_property
    def items_play(self):
        return self.items_play_local + self.get_players(f'play_{self.mode_type}')

    @cached_property
    def items_search(self):
        return self.get_players(f'search_{self.mode_type}')

    @property
    def items(self):
        return self.items_play + self.items_search


class PlayerItemsEpisode(PlayerItemsMovie):
    tmdb_type = 'tv'
    mode_type = 'episode'
    local_item_class = PlayerItemLocalEpisode


def PlayerItems(tmdb_type, *args, **kwargs):
    routes = {
        'movie': PlayerItemsMovie,
        'tv': PlayerItemsEpisode,
    }
    return routes[tmdb_type](*args, **kwargs)
