from jurialmunkey.ftools import cached_property
from jurialmunkey.parser import try_int
from tmdbhelper.lib.sync.itemdata import SyncItem, SyncItemData


class TMDbWatchlistItemData(SyncItemData):
    season_number = None
    episode_number = None
    notes = None

    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_tmdb_id(self):
        return self.item['id']

    @cached_property
    def title(self):
        return self.get_title()

    def get_title(self):
        return self.item['title'] if self.item_type == 'movie' else self.item['name']

    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        return self.item.get('release_date' if self.item_type == 'movie' else 'first_air_date') or None

    @cached_property
    def year(self):
        return self.get_year()

    def get_year(self):
        return try_int(self.premiered[:4]) if self.premiered else None


class TMDbWatchlistItem(SyncItem):
    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'title', 'year', 'premiered',
    )

    @cached_property
    def items(self):
        return self.get_items()

    def get_items(self):
        return [self.get_item(meta, rank) for rank, meta in enumerate(self.meta, 1)]

    def get_item(self, meta, rank):
        item = TMDbWatchlistItemData(meta, self.item_type)
        item.rank = rank
        # TMDb does not return added-at dates. Retain the local first-seen date.
        item.listed_at = self.first_seen.get(item.item_id) or self.synced_at
        return item

    def get_data(self):
        return {item.item_id: [getattr(item, key) for key in self.keys] for item in self.items}
