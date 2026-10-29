from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.items.itemlist import ItemMappingBasicFactory


class CurrentlyWatchingItemMapper(ItemMapper):
    @cached_property
    def episode_numbers(self):
        return self.get_episode_numbers()

    def get_episode_numbers(self):
        if self.meta.get('next_episode_id'):
            return self.meta['next_episode_id'].split('.')[2:4]
        return (self.meta['season_number'], self.meta['episode_number'])

    @cached_property
    def mapped_item(self):
        return self.get_mapped_item()

    def get_mapped_item(self):
        season, episode = self.episode_numbers
        return ItemMappingBasicFactory({
            'id': self.meta['tmdb_id'],
            'title': self.meta['title'],
            'season': season,
            'episode': episode,
        }, item_type='episode').get_item()

    @cached_property
    def label(self):
        return self.mapped_item['label']

    def get_infolabels(self):
        return self.mapped_item['infolabels']

    def get_unique_ids(self):
        return self.mapped_item['unique_ids']

    def get_params(self):
        return self.mapped_item['params']

    def get_item(self):
        item = super().get_item()
        item['path'] = self.mapped_item['path']
        return item


class CurrentlyWatchingMovieItemMapper(CurrentlyWatchingItemMapper):
    def get_mapped_item(self):
        return ItemMappingBasicFactory({
            'id': self.meta['tmdb_id'],
            'title': self.meta['title'],
        }, item_type='movie').get_item()


def FactoryCurrentlyWatchingItemMapper(meta, add_infoproperties=None):
    mapper_class = CurrentlyWatchingMovieItemMapper if meta['item_type'] == 'movie' else CurrentlyWatchingItemMapper
    return mapper_class(meta, add_infoproperties)
