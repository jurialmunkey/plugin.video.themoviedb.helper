from tmdbhelper.lib.script.sync.menu import Menu as BasicMenu


class Menu(BasicMenu):
    items = {}


def sync_tmdb_user_item(tmdb_type, tmdb_id, season=None, episode=None, sync_type=None):
    menu = Menu(tmdb_type, tmdb_id, season, episode)
    menu.select(sync_type)
