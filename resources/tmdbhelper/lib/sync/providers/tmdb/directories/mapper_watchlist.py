from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import ADDONPATH, get_localized
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper


class TMDbWatchlistMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.get_label()

    def get_label(self):
        return get_localized(32193)

    def get_params(self):
        return {
            'info': 'tmdb_v4_watchlist', 'tmdb_type': 'both',
            'list_name': self.label, 'plugin_category': self.label,
        }

    def get_art(self):
        return {
            'icon': f'{ADDONPATH}/resources/icons/themoviedb/watchlist.png',
            'fanart': f'{ADDONPATH}/fanart.jpg',
        }
