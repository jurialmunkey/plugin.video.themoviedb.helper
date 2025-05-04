import random
from tmdbhelper.lib.addon.plugin import get_setting, convert_type, get_localized
from tmdbhelper.lib.items.directories.tmdb.lists_related import ListRecommendations
from tmdbhelper.lib.items.directories.trakt.lists_sync import ListSync


class ListRandomBecauseYouWatched(ListRecommendations):
    def get_items(self, info, tmdb_type, **kwargs):

        watched_items = ListSync(self.handle, self.paramstring).get_list_items(
            sync_type='watched',
            item_type=convert_type(tmdb_type, 'trakt'),
            page=1,
            limit=get_setting('trakt_becausewatchedseed', 'int') or 5,
            next_page=False,
            params=None,
            sort_by='plays' if info == 'trakt_becausemostwatched' else 'watched',
            sort_how='desc'
        )
        if not watched_items:
            return

        item = watched_items[random.randint(0, len(watched_items) - 1)]

        try:
            label = item['label']
            tmdb_type = item['params']['tmdb_type']
            tmdb_id = item['params']['tmdb_id']
        except (AttributeError, KeyError):
            return

        params = {
            'info': 'recommendations',
            'tmdb_type': tmdb_type,
            'tmdb_id': tmdb_id,
        }

        items = super().get_items(**params)

        self.plugin_category = f'{get_localized(32288)} ({label})'

        return items
