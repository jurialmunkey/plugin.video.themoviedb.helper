from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.sync.itemdata import SyncItem, SyncItemData


class TraktSyncItemData(SyncItemData):
    @cached_property
    def metadata(self):
        return self.get_metadata()

    def get_metadata(self):
        return self.item[self.parent_item_type]

    @cached_property
    def tmdb_id(self):
        return self.get_tmdb_id()

    def get_tmdb_id(self):
        return self.metadata['ids'].get('tmdb')

    @cached_property
    def season_number(self):
        return self.get_season_number()

    def get_season_number(self):
        if self.item_type == 'season':
            return self.item['season']['number']
        if self.item_type == 'episode':
            return self.item['episode']['season']

    @cached_property
    def episode_number(self):
        return self.get_episode_number()

    def get_episode_number(self):
        if self.item_type == 'episode':
            return self.item['episode']['number']

    @cached_property
    def premiered(self):
        return self.get_premiered()

    def get_premiered(self):
        try:
            return self.metadata['released' if self.parent_item_type == 'movie' else 'first_aired'][:10]
        except (KeyError, TypeError):
            return

    @cached_property
    def values(self):
        return self.get_values()

    def get_values(self):
        values = dict(self.item)
        values.update((key, self.metadata.get(key)) for key in (
            'year', 'title', 'status', 'country', 'certification', 'runtime'))
        values.update(
            item_type=self.item_type, tmdb_type=self.tmdb_type, tmdb_id=self.tmdb_id,
            season_number=self.season_number, episode_number=self.episode_number,
            trakt_slug=self.metadata['ids'].get('slug'), premiered=self.premiered,
            trakt_rating=self.metadata.get('rating'), trakt_votes=self.metadata.get('votes'))
        return values


class TraktSyncItem(SyncItem):
    _additional_keys = (
        'item_type', 'tmdb_type', 'tmdb_id', 'season_number', 'episode_number',
        'trakt_slug', 'premiered', 'year', 'title', 'status', 'country', 'certification', 'runtime',
        'trakt_rating', 'trakt_votes',
    )

    def get_item_data(self, item):
        return TraktSyncItemData(item, item.get('type') or self.item_type)

    def get_data(self):
        return {item.item_id: [item.values.get(key) for key in self.keys]
                for item in (self.get_item_data(meta) for meta in self.meta)}
