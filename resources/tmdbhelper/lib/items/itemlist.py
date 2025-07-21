from jurialmunkey.parser import get_params
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.plugin import PLUGINPATH, convert_trakt_type, convert_type, get_setting
from tmdbhelper.lib.items.filters import is_excluded
from tmdbhelper.lib.items.pages import PaginatedItems
from collections import namedtuple


PaginatedItemsTuple = namedtuple("PaginatedItemsTuple", "items next_page")


PARAMS_DEF = {
    'episode': {
        'info': 'details', 'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}',
        'season': '{season}', 'episode': '{episode}'
    },
    'season': {
        'info': 'episodes', 'tmdb_type': 'tv', 'tmdb_id': '{tmdb_id}',
        'season': '{season}'
    }
}


class ItemMapping():
    """ Base class for inheritance in item mappers """

    def __init__(self, item, item_type=None, params_def=None):
        self.item = item
        self.item_type = item_type
        self.tmdb_type = convert_trakt_type(self.item_type)
        self.dbtype = convert_type(self.tmdb_type, 'dbtype')
        self.params_def = (params_def or {}).get(item_type) or PARAMS_DEF.get(item_type)


class ItemMappingBasic(ItemMapping):
    """ Mapping for individual items in a list of items """

    @cached_property
    def unique_ids(self):
        return self.get_unique_ids()

    @cached_property
    def infolabels(self):
        return self.get_infolabels()

    def get_unique_ids(self, unique_ids=None):
        unique_ids = unique_ids or {}
        unique_ids['tmdb'] = self.item.get('id')
        unique_ids['imdb'] = self.item.get('imdb_id')
        return unique_ids

    def get_infolabels(self, infolabels=None):
        infolabels = {}
        infolabels['title'] = self.item.get('title')
        infolabels['year'] = self.item.get('release_year')
        infolabels['mediatype'] = self.dbtype
        return infolabels

    def get_item(self):
        base_item = {}
        base_item['label'] = self.item.get('title') or ''
        base_item['unique_ids'] = self.unique_ids
        base_item['infolabels'] = self.infolabels
        base_item['params'] = get_params(self.item, self.tmdb_type, definition=self.params_def)
        base_item['path'] = PLUGINPATH
        return base_item


class ItemMappingBasicSeason(ItemMappingBasic):
    def get_unique_ids(self, unique_ids=None):
        unique_ids = super().get_unique_ids()
        unique_ids['tvshow.tmdb'] = self.item.get('id')
        return unique_ids

    def get_infolabels(self, infolabels=None):
        infolabels = super().get_infolabels()
        infolabels['season'] = self.item.get('season')
        return infolabels


class ItemMappingBasicEpisode(ItemMappingBasicSeason):
    def get_infolabels(self, infolabels=None):
        infolabels = super().get_infolabels()
        infolabels['episode'] = self.item.get('episode')
        return infolabels


def ItemMappingBasicFactory(item, item_type=None, params_def=None):
    routes = {
        'season': ItemMappingBasicSeason,
        'episode': ItemMappingBasicEpisode,
    }
    try:
        route = routes[item_type]
    except KeyError:
        route = ItemMappingBasic
    return route(item, item_type=item_type, params_def=params_def)


class ItemMappingTrakt(ItemMapping):
    """ Conversion to Trakt style metadata """

    def get_item(self):
        base_item = {}
        base_item['rank'] = self.item.get('rank') or ''
        base_item['type'] = self.item_type
        main_item = base_item.setdefault(self.item_type, {})
        main_item['title'] = self.item.get('title') or ''
        main_item['year'] = self.item.get('release_year') or ''
        uids_item = main_item.setdefault('ids', {})
        uids_item['imdb'] = self.item.get('imdb_id') or ''
        uids_item['tvdb'] = self.item.get('tvdb_id') or ''
        uids_item['tmdb'] = self.item.get('id') or ''
        return base_item


class ItemListPaginationBasic():
    """ Paginates and configures items in a list. Base class for inheritance """

    def __init__(self, meta, page=1, limit: int = None):
        self.meta = meta
        self.page = page
        self.limit = limit or (20 * max(get_setting('pagemulti_trakt', 'int'), 1))

    @cached_property
    def paginated_items(self):
        if self.limit is None:
            return PaginatedItemsTuple(self.meta, [])
        return PaginatedItems(self.meta, page=self.page, limit=self.limit)

    @property
    def next_page(self):
        return self.paginated_items.next_page


class ItemListPagination(ItemListPaginationBasic):
    """ Paginates and configures items in a list of items """

    def __init__(
            self, meta,
            page: int = 1,
            limit: int = None,
            permitted_types: tuple = None,
            params_def: dict = None,
            filters: dict = None,
            trakt_style: bool = False):
        super(ItemListPagination, self).__init__(meta, page=page, limit=limit)
        self.meta = [i for k, v in meta.items() for i in v if i]  # Join all content types together to mimic Trakt style combined lists TODO: Add a filter
        self.permitted_types = permitted_types or ('movie', 'show', 'season', 'episode')
        self.params_def = params_def
        self.filters = filters
        self.trakt_style = trakt_style

    @property
    def items(self):
        return self.paginated_items_dict.get('items') or []

    @property
    def movies(self):
        return self.paginated_items_dict.get('movies') or []

    @property
    def shows(self):
        return self.paginated_items_dict.get('shows') or []

    @property
    def seasons(self):
        return self.paginated_items_dict.get('seasons') or []

    @property
    def episodes(self):
        return self.paginated_items_dict.get('episodes') or []

    @property
    def item_maker(self):
        if self.trakt_style:
            return ItemMappingTrakt
        return ItemMappingBasicFactory

    @cached_property
    def paginated_items_dict(self):
        paginated_items_dict = {'items': []}
        paginated_items_dict_items_append = paginated_items_dict['items'].append

        for i in self.paginated_items.items:
            item_type = i.get('mediatype', None)

            if self.permitted_types and item_type not in self.permitted_types:
                continue

            if self.filters and is_excluded(i, **self.filters):
                continue

            item = self.item_maker(i, item_type=item_type, params_def=self.params_def).get_item()

            if not item:
                continue

            # Also add item to a list only containing that item type
            # Useful if we need to only get one type of item from a mixed list (e.g. only "movies")
            paginated_items_dict.setdefault(f'{item_type}s', []).append(item)
            paginated_items_dict_items_append(item)

        paginated_items_dict['next_page'] = self.next_page
        return paginated_items_dict
