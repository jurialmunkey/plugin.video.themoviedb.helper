from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import get_localized
from tmdbhelper.lib.items.directories.mapper_basic import ItemMapper
from tmdbhelper.lib.sync.providers.monitor_lists import MonitorListsSupplier


class TMDbMonitorListMapper(ItemMapper):
    @cached_property
    def label(self):
        return self.get_label()

    def get_label(self):
        return f'TMDb: {self.meta["name"]}'

    def get_params(self):
        return {'user_slug': '__api_tmdb__', 'list_slug': self.meta['reference']}


class TMDbLibraryItem:
    def __init__(self, meta, tmdb_type):
        self.meta = meta
        self.tmdb_type = tmdb_type

    @property
    def item_type(self):
        return {'movie': 'movie', 'tv': 'show'}[self.tmdb_type]

    @cached_property
    def item(self):
        return self.get_item()

    def get_item(self):
        title = self.meta['title'] if self.tmdb_type == 'movie' else self.meta['name']
        return {
            'type': self.item_type,
            self.item_type: {'title': title, 'ids': {'tmdb': self.meta['id'], 'imdb': None}},
        }


class TMDbMonitorLists(MonitorListsSupplier):
    item_mapper_class = TMDbMonitorListMapper
    account_lists = (
        ('watchlist', 32193), ('favorites', 1036),
        ('rated', 32521), ('recommendations', 32223),
    )

    def get_mapped_item(self, item, add_infoproperties=None):
        return self.item_mapper_class(item, add_infoproperties).item

    def get_account_lists(self):
        return [self.get_mapped_item({
            'name': f'{get_localized(label)} {get_localized(type_label)}',
            'reference': f'{list_type}/{tmdb_type}',
        }) for list_type, label in self.account_lists
            for tmdb_type, type_label in (('movie', 20342), ('tv', 20343))]

    def get_lists(self):
        if not self.provider.is_user_authorized:
            return []
        owned = self.provider.user_lists.get_owned_lists()
        return self.get_account_lists() + [self.get_mapped_item({
            'name': item['name'], 'reference': f'list/{item["id"]}',
        }) for item in (owned or [])]

    def get_list_items(self, list_slug):
        if not self.provider.is_user_authorized:
            return
        list_type, reference = list_slug.split('/', 1)
        if list_type == 'list':
            entries = self.provider.user_lists.get_list_items(reference)
            return self.get_library_items(entries)
        if list_type not in dict(self.account_lists) or reference not in ('movie', 'tv'):
            raise ValueError(f'Invalid TMDb monitored list: {list_slug}')
        entries = self.provider.user_lists.get_account_items(reference, list_type)
        return self.get_library_items(entries, reference)

    @staticmethod
    def get_library_items(entries, tmdb_type=None):
        if entries is None:
            return
        return [TMDbLibraryItem(item, tmdb_type or item['media_type']).item for item in entries]
