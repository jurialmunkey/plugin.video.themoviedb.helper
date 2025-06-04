import random
from tmdbhelper.lib.addon.plugin import get_setting, get_localized
from tmdbhelper.lib.items.directories.tmdb.lists_related import ListRecommendations
from tmdbhelper.lib.items.directories.trakt.lists_sync import ListMostWatched, ListHistory


class ListRandomBecauseYouWatched(ListRecommendations):
    def get_items(self, info, tmdb_type, **kwargs):

        func = ListMostWatched if info == 'trakt_becausemostwatched' else ListHistory

        watched_items = func(-1, self.paramstring)
        watched_items.list_properties.next_page = False
        watched_items = watched_items.get_items(tmdb_type=tmdb_type)

        if not watched_items:
            return

        limit = get_setting('trakt_becausewatchedseed', 'int') or 5
        watched_items = watched_items[:limit]

        item = watched_items[random.randint(0, len(watched_items) - 1)]

        try:
            label = item['label']
            tmdb_type = item['params']['tmdb_type']
            tmdb_id = item['params']['tmdb_id']
        except (AttributeError, KeyError):
            return

        localized = get_localized(32288)

        params = {
            'info': 'recommendations',
            'tmdb_type': tmdb_type,
            'tmdb_id': tmdb_id,
        }

        items = super().get_items(**params)

        self.plugin_category = f'{localized} {label}'
        self.property_params.update(
            {
                'widget.label': label,
                'widget.tmdb_type': tmdb_type,
                'widget.tmdb_id': tmdb_id,
                'widget.category': localized,
            }
        )

        return items
