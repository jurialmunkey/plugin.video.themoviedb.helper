from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.mapper_nextepisodes import NextEpisodeItemMapper
from tmdbhelper.lib.sync.datasync import SyncDataFactory


class ListNextEpisodesProperties:
    """Replace show entries after list caching and before item detail enrichment."""

    item_mapper_class = NextEpisodeItemMapper

    def __init__(self, items, container_content):
        self.source_items = items
        self.source_content = container_content

    @cached_property
    def container_content(self):
        return self.get_container_content()

    def get_container_content(self):
        return 'episodes' if self.source_content == 'tvshows' else self.source_content

    @cached_property
    def next_episode_ids(self):
        return self.get_next_episode_ids()

    def get_next_episode_ids(self):
        getter = SyncDataFactory().get_all_unhidden_shows_nextepisode_getter()
        return {str(item['tmdb_id']): item['next_episode_id'] for item in getter.items}

    def get_entry(self, item):
        unique_ids = item['unique_ids']
        tmdb_id = unique_ids.get('tmdb') or unique_ids['tvshow.tmdb']
        return {
            'tmdb_id': tmdb_id,
            'title': item['infolabels'].get('title') or item.get('label') or '',
            'next_episode_id': self.next_episode_ids.get(str(tmdb_id)),
        }

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    def get_item(self, item):
        if (item.get('infolabels') or {}).get('mediatype') != 'tvshow':
            return item
        return self.get_mapped_item(self.get_entry(item))

    @cached_property
    def finalised_items(self):
        return self.get_finalised_items()

    def get_finalised_items(self):
        if not self.source_items:
            return self.source_items
        return [self.get_item(item) for item in self.source_items]
